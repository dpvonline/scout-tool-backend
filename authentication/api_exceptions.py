from rest_framework import status
from rest_framework.exceptions import APIException
from django.utils.encoding import force_str


class NoGroupId(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'Keine Gruppen Id angegeben.'
    default_code = 'no_group_id'


class KeycloakError(APIException):
    status_code = 400
    default_detail = "{error}"
    default_code = 'keycloak_error'

    def __init__(self, error, detail=None, code=None):
        if detail is None:
            detail = force_str(self.default_detail).format(error=error)
        super().__init__(detail, code)
