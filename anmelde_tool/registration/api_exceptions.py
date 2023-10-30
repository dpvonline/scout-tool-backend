from rest_framework.exceptions import APIException


class ZipCodeNotFound(APIException):
    status_code = 404
    default_detail = 'Die angegebene PLZ wurde nicht gefunden.'
    default_code = 'not_found'


class ParticipantAlreadyExists(APIException):
    status_code = 400
    default_detail = 'Teilnehmer ist bereits angemeldet.'
    default_code = 'bad request'
