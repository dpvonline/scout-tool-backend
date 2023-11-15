from rest_framework.exceptions import APIException


class ParticipantAlreadyExists(APIException):
    status_code = 400
    default_detail = 'Teilnehmer ist bereits angemeldet.'
    default_code = 'bad request'
