from django.db.models import QuerySet, Count
from rest_framework import mixins, viewsets, status
from rest_framework.response import Response
from django.http import JsonResponse

from anmelde_tool.event import api_exceptions
from anmelde_tool.event import permissions as event_permissions
from anmelde_tool.event.helper import filter_registration_by_leadership
from anmelde_tool.event.summary.kpi import serializers as kpi_serializers
from anmelde_tool.registration.models import Registration, RegistrationParticipant
from anmelde_tool.registration import serializers as registration_serializers
from anmelde_tool.registration import models as registration_models
from anmelde_tool.event import models as event_models


class TotalParticipantsViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    permission_classes = [event_permissions.IsSubEventResponsiblePerson | event_permissions.IsLeaderPerson]

    def list(self, request, *args, **kwargs) -> Response:
        registrations: QuerySet[Registration] = self.get_queryset()
        num = registrations.aggregate(count=Count('registrationparticipant'))['count'] or 0
        return Response(num, status=status.HTTP_200_OK)

    def get_queryset(self) -> QuerySet[Registration]:
        event_id = self.kwargs.get("event_pk", None)

        registrations = Registration.objects.filter(event=event_id)
        registrations = filter_registration_by_leadership(self.request, event_id, registrations)

        return registrations


class TotalRegistrationsViewSet(TotalParticipantsViewSet):
    def list(self, request, *args, **kwargs) -> Response:
        registrations: QuerySet[Registration] = self.get_queryset()
        num = registrations.count() or 0

        return Response(num, status=status.HTTP_200_OK)


class LastRegistrationsViewSet(TotalParticipantsViewSet):
    def list(self, request, *args, **kwargs) -> Response:
        registrations: QuerySet[Registration] = self.get_queryset()
        registrations = registrations.annotate(count=Count('registrationparticipant')).order_by('-created_at')
        result = registrations[:5]

        serializer = kpi_serializers.RegistrationEventKPISerializer(result, many=True, read_only=True)

        return Response(serializer.data, status=status.HTTP_200_OK)


class LargestRegistrationsViewSet(TotalParticipantsViewSet):
    def list(self, request, *args, **kwargs) -> Response:
        registrations: QuerySet[Registration] = self.get_queryset()
        registrations = registrations.annotate(count=Count('registrationparticipant')).order_by('-count')
        result = registrations[:5]

        serializer = kpi_serializers.RegistrationEventKPISerializer(result, many=True, read_only=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class BookingOptionViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    def get_queryset(self) -> QuerySet:
        event_id = self.kwargs.get("event_pk", None)
        return event_models.BookingOption.objects.filter(event=event_id)

    def list(self, request, *args, **kwargs) -> Response:
        booking_options: QuerySet[registration_models.BookingOption] = self.get_queryset()
        serializer = kpi_serializers.BookingOptionKPISerializer(booking_options, many=True, read_only=True)

        return Response(serializer.data, status=status.HTTP_200_OK)
