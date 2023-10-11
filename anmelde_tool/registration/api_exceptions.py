from rest_framework.exceptions import APIException


class ZipCodeNotFound(APIException):
    status_code = 404
    default_detail = 'Die angegebene PLZ wurde nicht gefunden.'
    default_code = 'not_found'


class PersonAlreadyRegistered(APIException):
    status_code = 404
    default_detail = 'Die angegebene Person wurde bereits angemeldet.'
    default_code = 'already_registered'
