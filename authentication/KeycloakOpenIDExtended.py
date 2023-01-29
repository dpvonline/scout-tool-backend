from keycloak import KeycloakOpenID, urls_patterns
from keycloak.exceptions import raise_error_from_response, KeycloakGetError

URL_ALL_USERS = "admin/realms/{realm-name}/users"
URL_GROUP_USERS = "admin/realms/{realm-name}/groups/{group-id}/members"


class KeycloakOpenIDExtended(KeycloakOpenID):

    def get_all_users(self, token):
        params_path = {"realm-name": self.realm_name}
        self.connection.add_param_headers('Authorization', f'Bearer {token}')
        data_raw = self.connection.raw_get(URL_ALL_USERS.format(**params_path))
        return raise_error_from_response(data_raw, KeycloakGetError)

    def get_group_users(self, token: str, group_id: str):
        params_path = {'realm-name': self.realm_name, 'group-id': group_id}
        self.connection.add_param_headers('Authorization', token)
        data_raw = self.connection.raw_get(URL_GROUP_USERS.format(**params_path))
        return raise_error_from_response(data_raw, KeycloakGetError)

    def get_user_groups(self, token: str, user_id: str, brief_representation: str = True):
        """Get user groups.

        Returns a list of groups of which the user is a member

        :param token: auth token of user
        :type token:str
        :param user_id: User id
        :type user_id: str
        :param brief_representation: whether to omit attributes in the response
        :type brief_representation: bool
        :return: a list of group the user is in
        :rtype: list
        """
        params = {"briefRepresentation": brief_representation}
        params_path = {"realm-name": self.realm_name, "id": user_id}
        self.connection.add_param_headers('Authorization', token)
        data_raw = self.connection.raw_get(
            urls_patterns.URL_ADMIN_USER_GROUPS.format(**params_path), **params
        )
        return raise_error_from_response(data_raw, KeycloakGetError)
