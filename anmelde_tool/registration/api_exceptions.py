from rest_framework.exceptions import APIException


class ParticipantAlreadyExists(APIException):
    status_code = 400
    default_detail = 'Teilnehmer ist bereits für diese Veranstaltung angemeldet. Eventuell von einem anderem Stamm.'
    default_code = 'bad request'
