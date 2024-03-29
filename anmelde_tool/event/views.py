from copy import deepcopy
from queue import Queue

from django.db.models import Q, QuerySet
from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, status, mixins
from rest_framework.exceptions import NotFound, MethodNotAllowed
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.filters import SearchFilter

from anmelde_tool.attributes.models import AttributeModule
from anmelde_tool.event import api_exceptions as event_api_exceptions
from anmelde_tool.event import helper as event_helper
from anmelde_tool.event import models as event_models
from anmelde_tool.event import permissions as event_permissions
from anmelde_tool.event import serializers as event_serializers
from anmelde_tool.event.models import StandardEventTemplate, Event, EventModule, EventLocation
from anmelde_tool.event.permissions import EventRole, check_event_permission
from basic.helper.get_property_ids import get_zipcode
from keycloak_auth.helper import get_groups_of_user
from keycloak_auth.models import KeycloakGroup


def add_event_attribute(attribute_module: AttributeModule, event_module: EventModule) -> AttributeModule:
    new_attribute_module: AttributeModule = deepcopy(attribute_module)
    new_attribute_module.pk = None
    new_attribute_module.id = None
    new_attribute_module.standard = False
    new_attribute_module.event_module = event_module
    new_attribute_module.save()
    return new_attribute_module


def add_event_module(module: EventModule, event: Event) -> EventModule:
    new_module: EventModule = deepcopy(module)
    new_module.pk = None
    new_module.standard = False
    new_module.event = event
    new_module.save()
    for attribute_module in module.attributemodule_set.all():
        add_event_attribute(attribute_module, new_module)
    return new_module


class EventLocationViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = ('name',)
    queryset = EventLocation.objects.all()
    serializer_class = event_serializers.EventLocationSerializer

    def create(self, request, *args, **kwargs) -> Response:
        get_zipcode(request)
        return super().create(request, *args, **kwargs)

    def update(self, request, *args, **kwargs) -> Response:
        get_zipcode(request)
        return super().update(request, *args, **kwargs)


class EventModuleViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = EventModule.objects.all()
    serializer_class = event_serializers.EventModuleSerializer


class EventReadViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = event_serializers.EventReadSerializer

    def get_queryset(self):
        technical_name = self.request.query_params.get('technical_name', None)
        if technical_name is None:
            return Event.objects.all()
        return Event.objects.filter(technical_name=technical_name)


class MyInvitationsViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = event_serializers.MyInvitationsSerializer

    def get_queryset(self):
        token = self.request.META.get('HTTP_AUTHORIZATION')
        child_ids = get_groups_of_user(token, self.request.user.keycloak_id)
        if self.request.user.person.scout_group and self.request.user.person.scout_group.keycloak:
            child_ids += [self.request.user.person.scout_group.keycloak.keycloak_id]
        child_groups = KeycloakGroup.objects.filter(keycloak_id__in=child_ids).prefetch_related('parent')

        q = Queue()
        for group in child_groups:
            q.put(group)

        parent_ids = set()
        while not q.empty():
            group = q.get()
            parent_ids.add(group.id)
            if group.parent:
                q.put(group.parent)

        return Event.objects \
            .filter((Q(invited_groups__in=parent_ids) | Q(invited_groups=None)) & Q(is_public=True)) \
            .distinct()


class EventViewSet(viewsets.ModelViewSet):
    permission_classes = [event_permissions.IsEventSuperResponsiblePerson]
    queryset = Event.objects.all()
    serializer_class = event_serializers.EventCompleteSerializer

    def check_event_dates(self, request, event: Event) -> bool:
        edited = False
        start_date = request.data.get('start_date')
        if start_date is None:
            start_date = event.start_date
        else:
            edited = True

        end_date = request.data.get('end_date')
        if end_date is None:
            end_date = event.end_date
        else:
            edited = True

        registration_deadline = request.data.get('registration_deadline')
        if registration_deadline is None:
            registration_deadline = event.registration_deadline
        else:
            edited = True

        registration_start = request.data.get('registration_start')
        if registration_start is None:
            registration_start = event.registration_start
        else:
            edited = True

        last_possible_update = request.data.get('last_possible_update')
        if last_possible_update is None:
            last_possible_update = event.last_possible_update
        else:
            edited = True

        if not edited:
            return True

        if end_date < start_date:
            raise event_api_exceptions.EndBeforeStart
        if start_date <= last_possible_update:
            raise event_api_exceptions.StartBeforeLastChange
        if last_possible_update <= registration_deadline:
            raise event_api_exceptions.LastChangeBeforeRegistrationDeadline
        if registration_deadline < registration_start:
            raise event_api_exceptions.RegistrationDeadlineBeforeRegistrationStart
        return True

    def create(self, request, *args, **kwargs) -> Response:

        price = request.data.get('price', str(15.00))
        del request.data['price']

        if (request.data.get('responsible_persons') is None) | (request.data.get('responsible_persons', []) is []):
            request.data['responsible_persons'] = [request.user.email, ]

        serializer: event_serializers.EventPostSerializer = event_serializers.EventPostSerializer(data=request.data)
        if not serializer.is_valid(raise_exception=True):
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        self.check_event_dates(request, serializer.validated_data)

        event: Event = serializer.save()
        event.responsible_persons.add(request.user)

        if price:
            event_models.BookingOption.objects.create(
                name='Standard',
                price=float(str(price).replace(",", ".")),
                event=event,
            )

        standard_event: StandardEventTemplate = event_helper.custom_get_or_404(
            event_api_exceptions.SomethingNotFound('Standard Event 1'),
            event_models.StandardEventTemplate,
            pk=1
        )

        add_event_module(standard_event.introduction, event)
        add_event_module(standard_event.participants, event)
        add_event_module(standard_event.letter, event)
        add_event_module(standard_event.summary, event)

        for mapper in standard_event.other_required_modules.all():
            add_event_module(mapper, event)

        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs) -> Response:
        event: Event = self.get_object()
        self.check_event_dates(request, event)

        return super().update(request, *args, **kwargs)


class EventPartialUpdateViewSet(viewsets.ModelViewSet):
    '''
    You just need to provide the field which is to be modified.
    '''
    queryset = Event.objects.all()
    serializer_class = event_serializers.EventCompleteSerializer

    def put(self, request, *args, **kwargs):
        event: Event = self.get_object()
        self.check_event_dates(request, event)
        return self.partial_update(request, *args, **kwargs)


class BookingOptionViewSet(viewsets.ModelViewSet):
    permission_classes = [event_permissions.IsSubEventResponsiblePersonOrReadOnly]
    serializer_class = event_serializers.BookingOptionSerializer

    def get_queryset(self) -> QuerySet:
        event_id = self.kwargs.get("event_pk", None)
        if not event_helper.is_valid_uuid(event_id):
            raise event_api_exceptions.NoUUID(event_id)

        is_leader = check_event_permission(event_id, self.request) == EventRole.ADMIN_ROLE
        today = timezone.now()

        # handle bookable range
        if is_leader:
            booking_item = event_models.BookingOption.objects.filter(event=event_id)
        else:
            booking_item = event_models.BookingOption.objects.filter(
                Q(event=event_id)
                & (Q(bookable_from__lte=today) | Q(bookable_from__isnull=True))
                & (Q(bookable_till__gte=today) | Q(bookable_till__isnull=True))
            ).order_by(
                "bookable_from"
            )
        return booking_item

    def create(self, request, *args, **kwargs) -> Response:
        if request.data.get('name', None) is None:
            request.data['name'] = 'Standard'
        event_id = self.kwargs.get("event_pk", None)

        if event_id is None:
            raise NotFound()

        event = event_helper.get_event(event_id)

        request.data['event'] = event_id

        if request.data.get('bookable_till', None) is None:
            request.data['bookable_till'] = event.start_date

        request.data["price"] = float(str(request.data["price"]).replace(",", "."))

        return super().create(request, *args, **kwargs)

    def update(self, request, *args, **kwargs) -> Response:
        if request.data.get('name', None) is None:
            request.data['name'] = self.get_object().name
        request.data['event'] = self.get_object().event.id
        if request.data.get("price"):
            if isinstance(request.data["price"], str):
                request.data["price"] = float(request.data["price"].replace(",", "."))
            else:
                request.data["price"] = float(request.data["price"])
        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs) -> Response:
        if self.get_queryset().count() > 1:
            return super().destroy(request, *args, **kwargs)
        else:
            raise MethodNotAllowed(
                method='delete',
                detail=f'delete not allowed, because there must be at least one booking option'
            )


class AvailableEventModulesViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [event_permissions.IsSubEventSuperResponsiblePerson]
    serializer_class = event_serializers.EventModuleSerializer

    def get_queryset(self) -> QuerySet:
        event_id = self.kwargs.get("event_pk", None)
        mapper = EventModule.objects.filter(event=event_id).values_list('name', flat=True)
        return EventModule.objects.exclude(name__in=mapper).exclude(event__isnull=False).order_by('ordering')


class AssignedEventModulesViewSet(viewsets.ModelViewSet):
    permission_classes = [event_permissions.IsSubEventResponsiblePersonOrReadOnly]
    serializer_class = event_serializers.EventModuleSerializer

    def get_queryset(self) -> QuerySet:
        event_id = self.kwargs.get("event_pk", None)
        return EventModule.objects.filter(event=event_id).order_by('ordering')


class EventOverviewViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = event_serializers.EventOverviewSerializer

    def get_queryset(self) -> QuerySet:
        token = self.request.META.get('HTTP_AUTHORIZATION')
        child_ids = get_groups_of_user(token, self.request.user.keycloak_id)

        queryset = Event.objects.filter(
            Q(admin_group__keycloak_id__in=child_ids)
            | (Q(view_group__keycloak_id__in=child_ids) & Q(is_public=True))
            | Q(responsible_persons=self.request.user)
            | (Q(invited_groups=None) & Q(is_public=True))
            | Q(view_allow_subgroup=True)
        ).distinct()

        return queryset
