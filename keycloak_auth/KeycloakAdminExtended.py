import json
from typing import List

from keycloak import KeycloakAdmin
from keycloak.exceptions import raise_error_from_response, KeycloakGetError
from keycloak.urls_patterns import URL_ADMIN_CLIENT_AUTHZ_POLICIES, URL_ADMIN_CLIENT_AUTHZ_RESOURCES, \
    URL_ADMIN_GROUP_CHILD, URL_ADMIN_CLIENT, URL_ADMIN_CLIENT_AUTHZ_SCOPES

from keycloak_auth.dataclasses import PolicyBase, ResourceRepresentation, PolicyRoleRepresentation, PolicyRole, \
    PolicyAggregate
from keycloak_auth.enums import DecisionStrategy, Logic, PolicyType, PermissionType, jsonify

URL_ADMIN_CLIENT_AUTHZ_POLICIES_TYPE = URL_ADMIN_CLIENT + "/authz/resource-server/policy/{type}"
URL_ADMIN_CLIENT_AUTHZ_POLICIES_SEARCH = URL_ADMIN_CLIENT + "/authz/resource-server/policy/search"
URL_ADMIN_CLIENT_AUTHZ_PERMISSION = URL_ADMIN_CLIENT + "/authz/resource-server/permission/{type}"
URL_ADMIN_GROUP_COUNT = "admin/realms/{realm-name}/groups/count"


class KeycloakAdminExtended(KeycloakAdmin):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.realm_management_client_id = self.get_client_id('realm-management')

        manage_scopes = ['manage', 'manage-group-membership', 'manage-members', 'manage-membership']
        view_scopes = ['view-members', 'view']
        # Get scopes
        scopes = self.list_scopes(self.realm_management_client_id)
        self.scopes_manage_list = []
        self.scopes_view_list = []

        for scope in scopes:
            if scope['name'] in manage_scopes:
                self.scopes_manage_list.append(scope['id'])
            elif scope['name'] in view_scopes:
                self.scopes_view_list.append(scope['id'])
        self.scopes = self.scopes_view_list + self.scopes_manage_list

    def create_client_policy(self, client_id: str, payload: PolicyBase, skip_exists=False):
        params_path = {"realm-name": self.realm_name, "id": client_id, "type": payload.type.value}
        payload_json = jsonify(payload)
        data_raw = self.raw_post(URL_ADMIN_CLIENT_AUTHZ_POLICIES_TYPE.format(**params_path), data=payload_json)
        return raise_error_from_response(data_raw, KeycloakGetError, expected_codes=[201], skip_exists=skip_exists)

    def list_policies(self, client_id: str):
        params_path = {"realm-name": self.realm_name, "id": client_id}
        data_raw = self.raw_get(URL_ADMIN_CLIENT_AUTHZ_POLICIES.format(**params_path))
        return raise_error_from_response(data_raw, KeycloakGetError)

    def find_policy_by_name(self, client_id: str, name: str):
        params_path = {"realm-name": self.realm_name, "id": client_id}
        query = {'name': name}
        data_raw = self.raw_get(URL_ADMIN_CLIENT_AUTHZ_POLICIES_SEARCH.format(**params_path), **query)
        return raise_error_from_response(data_raw, KeycloakGetError)

    def create_permission(self, client_id: str, perm_type: str, payload: PolicyBase, skip_exists=False):
        params_path = {"realm-name": self.realm_name, "id": client_id, "type": perm_type}
        payload_json = jsonify(payload)
        data_raw = self.raw_post(URL_ADMIN_CLIENT_AUTHZ_PERMISSION.format(**params_path), data=payload_json)
        return raise_error_from_response(data_raw, KeycloakGetError, expected_codes=[201], skip_exists=skip_exists)

    def create_resource(self, client_id: str, payload: ResourceRepresentation, skip_exists=False):
        params_path = {"realm-name": self.realm_name, "id": client_id}
        payload_json = jsonify(payload)
        data_raw = self.raw_post(URL_ADMIN_CLIENT_AUTHZ_RESOURCES.format(**params_path), data=payload_json)
        return raise_error_from_response(data_raw, KeycloakGetError, expected_codes=[201], skip_exists=skip_exists)

    def list_resources(self, client_id: str, name: str):
        params_path = {"realm-name": self.realm_name, "id": client_id}
        query = {'name': name}
        data_raw = self.raw_get(URL_ADMIN_CLIENT_AUTHZ_RESOURCES.format(**params_path), **query)
        return raise_error_from_response(data_raw, KeycloakGetError)

    def list_scopes(self, client_id: str):
        params_path = {"realm-name": self.realm_name, "id": client_id}
        data_raw = self.raw_get(URL_ADMIN_CLIENT_AUTHZ_SCOPES.format(**params_path))
        return raise_error_from_response(data_raw, KeycloakGetError)

    def get_group_by_name(self, group_name):
        groups = self.get_groups()
        group = None
        for g in groups:
            if g['name'] == group_name:
                group = g
                break

        return group

    def move_group(self, payload: dict, parent: str):
        params_path = {"realm-name": self.realm_name, "id": parent, }
        data_raw = self.raw_post(URL_ADMIN_GROUP_CHILD.format(**params_path), data=json.dumps(payload))
        return raise_error_from_response(data_raw, KeycloakGetError, expected_codes=[204])

    def add_group_permissions(self, group):

        # Enable group permissions
        self.group_set_permissions(group_id=group['id'], enabled=True)

        # Get resource
        resource_name = f'group.resource.{group["id"]}'
        resource_representation = ResourceRepresentation(
            name=resource_name,
            displayName=f'Resource for group: {group["name"]}',
            ownerManagedAccess=False,
            type='Group',
            scopes=self.scopes
        )
        resource_representation_payload = jsonify(resource_representation, dumps=False)

        self.create_client_authz_resource(
            self.realm_management_client_id,
            payload=resource_representation_payload,
            skip_exists=True
        )
        server_resources = self.list_resources(client_id=self.realm_management_client_id, name=resource_name)

        # Generate manage permission
        manage_role, manage_policy = self.generate_permission(
            group,
            resource_name,
            server_resources,
            self.scopes_manage_list,
            PermissionType.MANAGE
        )

        # Generate view permission
        view_role, view_policy = self.generate_permission(
            group,
            resource_name,
            server_resources,
            self.scopes_view_list,
            PermissionType.VIEW
        )

        # Generate admin permission
        admin_role = self.generate_client_role(group, PermissionType.ADMIN)
        manage_policy_id = self.find_policy_by_name(self.realm_management_client_id, manage_policy)
        view_policy_id = self.find_policy_by_name(self.realm_management_client_id, view_policy)
        policies = [manage_policy_id['id'], view_policy_id['id']]
        _ = self.generate_client_aggregated_policy(
            group,
            policies,
            resource_name,
            PermissionType.ADMIN
        )

        # Assign permission to groups
        self.assign_group_client_roles(group['id'], self.realm_management_client_id, [view_role])
        self.assign_group_client_roles(group['id'], self.realm_management_client_id, [admin_role])

    def generate_permission(self,
                            group: dict,
                            resource_name: str,
                            server_resources: [],
                            scopes_list: [],
                            permission_type: PermissionType) -> [str, str]:

        # Create role
        client_role_json = self.generate_client_role(group, permission_type)

        # Create policy
        policy_name = self.generate_client_role_policy(group, client_role_json, resource_name, permission_type)

        # Create Permission
        self.generate_scope_permission(group, policy_name, scopes_list, server_resources, permission_type)

        return client_role_json, policy_name

    def generate_scope_permission(self,
                                  group: dict,
                                  policy_name: str,
                                  scopes_list: List[str],
                                  server_resources: List[str],
                                  permission_type: PermissionType) -> None:
        server_policy = self.find_policy_by_name(client_id=self.realm_management_client_id, name=policy_name)
        permission_name = f'{group["id"]}-{permission_type.value}-permission'
        permission_description = f'{permission_type.value.title()} permission for {group["path"]}'
        permission = PolicyAggregate(
            decisionStrategy=DecisionStrategy.UNANIMOUS,
            logic=Logic.POSITIVE,
            name=permission_name,
            resources=[server_resources[0]['_id']],
            type=PolicyType.RESOURCE,
            policies=[server_policy['id']],
            scopes=scopes_list,
            description=permission_description
        )
        self.create_permission(
            client_id=self.realm_management_client_id,
            perm_type='scope',
            payload=permission,
            skip_exists=True
        )

    def generate_client_role_policy(self,
                                    group: dict,
                                    client_role_json: str,
                                    resource_name: str,
                                    permission_type: PermissionType) -> str:
        policy_name = f'{group["id"]}-{permission_type.value}-policy'
        policy_description = f'{permission_type.value.title()} policy for {group["path"]}'
        roles = [PolicyRoleRepresentation(id=client_role_json['id'])]
        policy = PolicyRole(
            decisionStrategy=DecisionStrategy.UNANIMOUS,
            logic=Logic.POSITIVE,
            name=policy_name,
            resources=[resource_name],
            type=PolicyType.ROLE,
            roles=roles,
            description=policy_description
        )
        self.create_client_policy(client_id=self.realm_management_client_id, payload=policy, skip_exists=True)
        return policy_name

    def generate_client_aggregated_policy(self,
                                          group: dict,
                                          policies: List[str],
                                          resource_name: str,
                                          permission_type: PermissionType) -> str:
        policy_name = f'{group["id"]}-{permission_type.value}-policy'
        policy_description = f'{permission_type.value.title()} policy for {group["path"]}'
        policy = PolicyAggregate(
            decisionStrategy=DecisionStrategy.UNANIMOUS,
            logic=Logic.POSITIVE,
            name=policy_name,
            resources=[resource_name],
            type=PolicyType.AGGREGATE,
            policies=policies,
            description=policy_description
        )
        self.create_client_policy(client_id=self.realm_management_client_id, payload=policy, skip_exists=True)
        return policy_name

    def generate_client_role(self, group: dict, permission_type: PermissionType) -> str:
        client_role_name = f'group-{group["id"]}-{permission_type.value}-role'
        payload = {
            'name': client_role_name,
            'description': f'{permission_type.value.title()} role for group {group["path"]}'
        }
        self.create_client_role(client_role_id=self.realm_management_client_id, payload=payload, skip_exists=True)
        client_role = self.get_client_role(client_id=self.realm_management_client_id, role_name=client_role_name)
        return client_role

    def groups_count(self, query=None):
        """Count users.

        https://www.keycloak.org/docs-api/18.0/rest-api/index.html#_users_resource

        :param query: (dict) Query parameters for users count
        :type query: dict

        :return: counter
        :rtype: int
        """
        query = query or dict()
        params_path = {"realm-name": self.realm_name}
        data_raw = self.raw_get(URL_ADMIN_GROUP_COUNT.format(**params_path), **query)
        return raise_error_from_response(data_raw, KeycloakGetError)
