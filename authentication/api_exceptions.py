from rest_framework import status
from rest_framework.exceptions import APIException


class NoGroupId(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'Keine Gruppen Id angegeben.'
    default_code = 'no_group_id'
