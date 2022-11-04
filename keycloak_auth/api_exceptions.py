from rest_framework import status
from rest_framework.exceptions import APIException


class NoGroupId(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'Keine Gruppen Id angegeben.'
    default_code = 'no_group_id'


class AlreadyInGroup(APIException):
    status_code = status.HTTP_405_METHOD_NOT_ALLOWED
    default_detail = 'Du bist bereits in der Gruppe.'
    default_code = 'already_in_group'


class AlreadyAccessRequested(APIException):
    status_code = status.HTTP_405_METHOD_NOT_ALLOWED
    default_detail = 'Du hast bereits einen Antrag für diese Gruppe erstellt.'
    default_code = 'already_access_requested'
