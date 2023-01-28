from django.utils.encoding import force_str
from rest_framework import status
from rest_framework.exceptions import APIException


class NoGroupId(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'Keine Gruppen Id angegeben.'
    default_code = 'no_group_id'


class WrongParentGroupId(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'Die Id des Gruppen Kopfes existiert nicht.'
    default_code = 'wrong_group_id'


class AlreadyInGroup(APIException):
    status_code = status.HTTP_405_METHOD_NOT_ALLOWED
    default_detail = 'Du bist bereits in der Gruppe.'
    default_code = 'already_in_group'


class AlreadyAccessRequested(APIException):
    status_code = status.HTTP_405_METHOD_NOT_ALLOWED
    default_detail = 'Du hast bereits einen Antrag für diese Gruppe erstellt.'
    default_code = 'already_access_requested'


class NoKeycloakId(APIException):
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    default_detail = 'Es gibt einen Fehler in unserer Datenbasis. Wir konnten für {keycloak_group} keine Id finden.'
    default_code = 'no_keycloak_id'

    def __init__(self, keycloak_group: str, detail=None, code=None):
        if detail is None:
            detail = force_str(self.default_detail).format(keycloak_group=keycloak_group)
        super().__init__(detail, code)


class NotAuthorized(APIException):
    status_code = status.HTTP_403_FORBIDDEN
    default_detail = 'Du bist nicht berechtigt auf diese Ressource zuzugreifen.'
    default_code = 'forbidden'
