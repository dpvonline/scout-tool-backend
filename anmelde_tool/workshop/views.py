from django.contrib.auth import get_user_model
from django.db.models import QuerySet
from rest_framework import viewsets
from rest_framework.response import Response

from anmelde_tool.event import permissions as event_permissions
from anmelde_tool.workshop.models import Workshop
from anmelde_tool.workshop.serializer import WorkshopSerializer

User = get_user_model()


class WorkshopViewSet(viewsets.ModelViewSet):
    serializer_class = WorkshopSerializer
    permission_classes = [event_permissions.IsSubRegistrationResponsiblePerson]

    def create(self, request, *args, **kwargs) -> Response:
        if not request.data.get('supervisor'):
            request.data['supervisor'] = request.user.id

        request.data['registration'] = self.kwargs.get("registration_pk", None)
        return super().create(request, *args, **kwargs)

    def update(self, request, *args, **kwargs) -> Response:
        request.data['registration'] = self.get_object().registration.id
        return super().update(request, *args, **kwargs)

    def get_queryset(self) -> QuerySet:
        registration_id = self.kwargs.get("registration_pk", None)
        return Workshop.objects.filter(registration__id=registration_id)
