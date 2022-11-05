from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from anmelde_tool.event.choices import choices as event_choices
from basic.helper import choice_to_json


class RegistrationTypeGroupViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    def list(self, request) -> Response:
        result = choice_to_json(event_choices.RegistrationTypeGroup.choices)
        return Response(result, status=status.HTTP_200_OK)


class RegistrationTypeSingleViewSet(RegistrationTypeGroupViewSet):

    def list(self, request) -> Response:
        result = choice_to_json(event_choices.RegistrationTypeSingle.choices)
        return Response(result, status=status.HTTP_200_OK)


class LeaderTypesViewSet(RegistrationTypeGroupViewSet):

    def list(self, request) -> Response:
        result = choice_to_json(event_choices.LeaderTypes.choices)
        return Response(result, status=status.HTTP_200_OK)


class ScoutLevelTypesViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    def list(self, request) -> Response:
        result = choice_to_json(event_choices.ScoutLevelTypes.choices)
        return Response(result, status=status.HTTP_200_OK)


class FileTypeViewSet(RegistrationTypeGroupViewSet):

    def list(self, request) -> Response:
        result = choice_to_json(event_choices.FileType.choices)
        return Response(result, status=status.HTTP_200_OK)

class FileExtensionViewSet(RegistrationTypeGroupViewSet):

    def list(self, request) -> Response:
        result = choice_to_json(event_choices.FileExtension.choices)
        return Response(result, status=status.HTTP_200_OK)


class WorkshopTypeViewSet(RegistrationTypeGroupViewSet):

    def list(self, request) -> Response:
        result = choice_to_json(event_choices.WorkshopType.choices)
        return Response(result, status=status.HTTP_200_OK)
