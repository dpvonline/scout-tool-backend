from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from anmelde_tool.attributes.models import AttributeModule
from anmelde_tool.attributes.serializers import AttributeModuleSerializer
from basic.helper import choice_to_json
from anmelde_tool.attributes.choices import TravelType


class AttributeModuleViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = AttributeModuleSerializer
    queryset = AttributeModule.objects.all()


class TravelTypeViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    def list(self, request) -> Response:
        result = choice_to_json(TravelType.choices)
        return Response(result, status=status.HTTP_200_OK)
