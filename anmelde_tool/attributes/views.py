from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from . import models as attribute_models
from . import serializers as attribute_serializers
from .choices import TravelType


class AttributeViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = attribute_models.AbstractAttribute.objects.all()
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['type', 'type__name']

    def get_serializer_class(self):
        if self.action == 'create' or self.action == 'update':
            return attribute_serializers.AbstractAttributePostPolymorphicSerializer
        else:
            return attribute_serializers.AbstractAttributeGetPolymorphicSerializer


class AttributeTypeViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    def inheritors(self, klass) -> [str]:
        subclasses = set()
        work = [klass]
        while work:
            parent = work.pop()
            for child in parent.__subclasses__():
                if child not in subclasses:
                    subclasses.add(child.__name__)
                    work.append(child)
        return subclasses

    def list(self, request) -> Response:
        choices = self.inheritors(attribute_models.AbstractAttribute)
        return Response(choices, status=status.HTTP_200_OK)


class TravelTypeViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    def list(self, request) -> Response:
        return Response(TravelType.choices, status=status.HTTP_200_OK)
