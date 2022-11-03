import dataclasses
import json

from keycloak import KeycloakAdmin
from keycloak.exceptions import raise_error_from_response, KeycloakGetError
from keycloak.urls_patterns import URL_ADMIN_CLIENT_AUTHZ_POLICIES, URL_ADMIN_CLIENT_AUTHZ_RESOURCES, \
    URL_ADMIN_GROUP_CHILD, URL_ADMIN_CLIENT

from keycloak_auth.dataclasses import PolicyRoleRepresentation, PolicyRepresentation, ResourceRepresentation
from keycloak_auth.enums import DecisionStrategy, Logic, PolicyType, PermissionType, jsonify

URL_ADMIN_CLIENT_AUTHZ_POLICIES_TYPE = URL_ADMIN_CLIENT + "/authz/resource-server/policy/{type}"
URL_ADMIN_CLIENT_AUTHZ_POLICIES_SEARCH = URL_ADMIN_CLIENT + "/authz/resource-server/policy/search"
# URL_ADMIN_CLIENT_AUTHZ_RESOURCES = URL_ADMIN_CLIENT + "/authz/resource-server/resource"
URL_ADMIN_CLIENT_AUTHZ_SCOPES = URL_ADMIN_CLIENT + "/authz/resource-server/scope"
URL_ADMIN_CLIENT_AUTHZ_PERMISSION = URL_ADMIN_CLIENT + "/authz/resource-server/permission/{type}"


class KeycloakAdminExtended(KeycloakAdmin):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.realm_management_client_id = self.get_client_id('realm-management')
        # Get scopes
        scopes = self.list_scopes(self.realm_management_client_id)
        self.scopes_full_list = []
        self.scopes_view_list = []

        for scope in scopes:
            self.scopes_full_list.append(scope['id'])
            # if 'view' in scope['name']:
            self.scopes_view_list.append(scope['id'])

    def create_client_policy(self, client_id: str, payload: PolicyRepresentation, skip_exists=False):
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

    def create_permission(self, client_id: str, perm_type: str, payload: PolicyRepresentation, skip_exists=False):
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

    def move_group(self, payload, parent):
        params_path = {"realm-name": self.realm_name, "id": parent, }
        data_raw = self.raw_post(URL_ADMIN_GROUP_CHILD.format(**params_path), data=json.dumps(payload))
        return raise_error_from_response(data_raw, KeycloakGetError, expected_codes=[204])

    def add_group_permissions(self, group):

        # Enable group permissions
        self.group_set_permissions(group_id=group['id'], enabled=True)

        # Get resource
        resource_name = "group.resource." + group['id']
        server_resource = self.list_resources(client_id=self.realm_management_client_id, name=resource_name)

        # Generate admin permission
        admin_role = self.generate_permission(
            group,
            resource_name,
            server_resource,
            self.scopes_full_list,
            PermissionType.ADMIN
        )

        # Generate view permission
        view_role = self.generate_permission(
            group,
            resource_name,
            server_resource,
            self.scopes_view_list,
            PermissionType.VIEW
        )

        # Assign permission to groups
        self.assign_group_client_roles(group['id'], self.realm_management_client_id, [view_role])
        self.assign_group_client_roles(group['id'], self.realm_management_client_id, [admin_role])

    def generate_permission(self, group, resource_name, server_resource, scopes_list, permission_type: PermissionType):
        # Create role
        client_role_name = f'group-{group["id"]}-{permission_type.value}-role'
        payload = {
            'name': client_role_name,
            'description': f'{permission_type.value} role for group {group["path"]}'
        }
        self.create_client_role(client_role_id=self.realm_management_client_id, payload=payload, skip_exists=True)
        client_role_json = self.get_client_role(client_id=self.realm_management_client_id, role_name=client_role_name)

        # Create policy
        policy_name = f'{group["id"]}-{permission_type.value}-policy'
        policy_description = f'{permission_type.value} policy for {group["path"]}'
        roles = [PolicyRoleRepresentation.from_dict(client_role_json)]

        policy = PolicyRepresentation(
            decisionStrategy=DecisionStrategy.UNANIMOUS,
            logic=Logic.POSITIVE,
            name=policy_name,
            resources=[resource_name],
            type=PolicyType.ROLE,
            roles=roles,
            description=policy_description
        )
        self.create_client_policy(client_id=self.realm_management_client_id, payload=policy, skip_exists=True)
        server_policy = self.find_policy_by_name(client_id=self.realm_management_client_id, name=policy_name)

        permission_name = f'{group["id"]}-{permission_type.value}-permission'
        permission_description = f'{permission_type.value} permission for {group["path"]}'
        permission = PolicyRepresentation(
            decisionStrategy=DecisionStrategy.UNANIMOUS,
            logic=Logic.POSITIVE,
            name=permission_name,
            resources=[server_resource[0]['_id']],
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
        return client_role_json
