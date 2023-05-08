from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from anmelde_tool.attributes.choices import TravelType, AttributeType
from anmelde_tool.attributes.models import AttributeModule, BooleanAttribute, IntegerAttribute, FloatAttribute, \
    StringAttribute, TimeAttribute, TravelAttribute
from anmelde_tool.attributes.serializers import AttributeModuleSerializer, BooleanUpdateAttributeSerializer, \
    IntegerUpdateAttributeSerializer, FloatUpdateAttributeSerializer, TimeUpdateAttributeSerializer, \
    TravelUpdateAttributeSerializer, StringUpdateAttributeSerializer
from basic.helper import choice_to_json


class AttributeModuleViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = AttributeModuleSerializer
    queryset = AttributeModule.objects.all()


class BooleanAttributeViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = BooleanUpdateAttributeSerializer
    queryset = BooleanAttribute.objects.all()


class IntegerAttributeViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = IntegerUpdateAttributeSerializer
    queryset = IntegerAttribute.objects.all()


class FloatAttributeViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = FloatUpdateAttributeSerializer
    queryset = FloatAttribute.objects.all()


class StringAttributeViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = StringUpdateAttributeSerializer
    queryset = StringAttribute.objects.all()


class TravelAttributeViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = TravelUpdateAttributeSerializer
    queryset = TravelAttribute.objects.all()


class TimeAttributeViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = TimeUpdateAttributeSerializer
    queryset = TimeAttribute.objects.all()


class TravelTypeViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    def list(self, request) -> Response:
        result = choice_to_json(TravelType.choices)
        return Response(result, status=status.HTTP_200_OK)


class AttributeTypeViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    def list(self, request) -> Response:
        result = choice_to_json(AttributeType.choices)
        return Response(result, status=status.HTTP_200_OK)
