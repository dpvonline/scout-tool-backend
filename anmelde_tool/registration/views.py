from __future__ import annotations

import re
from datetime import timezone

from dateutil.relativedelta import relativedelta
from django.contrib.auth import get_user_model
from django.db.models import QuerySet
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import mixins, viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from anmelde_tool.attributes.choices import TravelType
from anmelde_tool.attributes.models import (
    AttributeModule,
    BooleanAttribute,
    StringAttribute,
    DateTimeAttribute,
    IntegerAttribute,
    FloatAttribute,
    TravelAttribute,
)
from anmelde_tool.attributes.serializers import (
    BooleanAttributePostSerializer,
    DateTimeAttributePostSerializer,
    StringAttributePostSerializer,
    FloatAttributePostSerializer,
    IntegerAttributePostSerializer,
    TravelAttributePostSerializer,
    BooleanAttributeSerializer,
    StringAttributeSerializer,
    IntegerAttributeSerializer,
    FloatAttributeSerializer,
    TravelAttributeSerializer,
    DateTimeAttributeSerializer,
)
from anmelde_tool.email_services import services
from anmelde_tool.event import api_exceptions as event_api_exceptions
from anmelde_tool.event import models as event_models
from anmelde_tool.event import permissions as event_permissions
from anmelde_tool.event.helper import get_registration, custom_get_or_404
from anmelde_tool.registration import serializers as registration_serializers
from anmelde_tool.registration.api_exceptions import ParticipantAlreadyExists
from anmelde_tool.registration.models import (
    Registration,
    RegistrationParticipant,
    RegistrationRating,
)
from authentication import models as auth_models
from basic import models as basic_models
from basic.helper.get_zipcode import get_zipcode_pk
from basic.models import ZipCode

User = get_user_model()


def create_missing_eat_habits(request) -> [str]:
    eat_habits = request.data.get("eat_habit", [])
    result = []
    if not eat_habits:
        return result
    for habit in eat_habits:
        if len(habit) > 100:
            raise event_api_exceptions.EatHabitTooLong
        splitted = re.split(",|;", habit)
        for split in splitted:
            split = split.strip().title()
            result.append(split)
            if not basic_models.EatHabit.objects.filter(name__exact=split).exists():
                basic_models.EatHabit.objects.create(name=split)
    return result


def get_attribute_params(kwargs, post_serializer):
    registration_id = kwargs.get("registration_pk")
    registration = get_object_or_404(Registration, id=registration_id)
    attribute_module_id = post_serializer.data["attribute_module"]
    attribute_module = get_object_or_404(AttributeModule, id=attribute_module_id)
    return attribute_module, registration


class RegistrationSingleParticipantViewSet(viewsets.ModelViewSet):
    permission_classes = [event_permissions.IsSubRegistrationResponsiblePerson]

    def get_queryset(self) -> QuerySet:
        registration_id = self.kwargs.get("registration_pk", None)
        return RegistrationParticipant.objects.filter(
            registration=registration_id
        ).order_by("age")

    def check_for_double_participants(self, request, event_id):
        if RegistrationParticipant.objects.filter(
                first_name=request.data.get("first_name"),
                last_name=request.data.get("last_name"),
                birthday=request.data.get("birthday"),
                registration__event=event_id).exists():
            raise ParticipantAlreadyExists()

    def create(self, request, *args, **kwargs) -> Response:
        zip_code = get_zipcode_pk(request)

        eat_habits_formatted = create_missing_eat_habits(request)
        if eat_habits_formatted and len(eat_habits_formatted) > 0:
            request.data["eat_habit"] = eat_habits_formatted
        elif "eat_habit" in request.data:
            del request.data["eat_habit"]

        zip_code_string = request.data.get("zip_code")
        zip_code_data = int(zip_code_string)

        registration: Registration = self.participant_initialization(request)
        event_id = registration.event.id
        self.check_for_double_participants(request, event_id)

        if request.data.get("age"):
            request.data["birthday"] = timezone.now() - relativedelta(
                years=int(request.data.get("age"))
            )
        request.data["registration"] = registration.id

        if (
                request.data.get("first_name") is None
                and request.data.get("last_name") is None
        ):
            max_num = self.get_queryset().count()
            request.data["first_name"] = "Teilnehmer"
            request.data["last_name"] = max_num + 1

        if request.data.get("booking_option") is None:
            request.data["booking_option"] = registration.event.bookingoption_set.first().id

        if request.data.get('allow_permanently'):
            person = auth_models.Person(
                first_name=request.data.get('first_name'),
                scout_name=request.data.get('scout_name'),
                last_name=request.data.get('last_name'),
                address=request.data.get('address'),
                birthday=request.data.get('birthday'),
                address_supplement=request.data.get('address_supplement'),
                scout_group=request.data.get('scout_group'),
                phone_number=request.data.get('phone_number'),
                email=request.data.get('email'),
                zip_code=zip_code,
                gender=request.data.get("gender"),
                scout_level="N",
            )
            person.save()
            person.created_by.add(self.request.user.id)

        return super().create(request, *args, **kwargs)

    def update(self, request, *args, **kwargs) -> Response:
        get_zipcode_pk(request)

        eat_habits_formatted = create_missing_eat_habits(request)

        if eat_habits_formatted and len(eat_habits_formatted) > 0:
            request.data["eat_habit"] = eat_habits_formatted
        elif "eat_habit" in request.data:
            del request.data["eat_habit"]

        registration: Registration = self.participant_initialization(request)
        event_id = registration.event.id
        # self.check_for_double_participants(request, event_id)

        request.data["generated"] = False
        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs) -> Response:
        registration: Registration = self.participant_initialization(request)

        return super().destroy(request, *args, **kwargs)

    def get_serializer_class(self):
        serializer = {
            "create": registration_serializers.RegistrationParticipantSerializer,
            "retrieve": registration_serializers.RegistrationParticipantSerializer,
            "list": registration_serializers.RegistrationParticipantShortSerializer,
            "update": registration_serializers.RegistrationParticipantSerializer,
            "destroy": registration_serializers.RegistrationParticipantSerializer,
        }
        return serializer.get(
            self.action, registration_serializers.RegistrationParticipantPutSerializer
        )

    def participant_initialization(self, request) -> Registration:
        input_serializer = (
            registration_serializers.RegistrationParticipantPutSerializer(
                data=request.data
            )
        )
        input_serializer.is_valid(raise_exception=True)

        registration_id = self.kwargs.get("registration_pk", None)
        registration: Registration = get_registration(registration_id)

        if not event_permissions.IsEventSuperResponsiblePerson:
            if registration.event.registration_start > timezone.now():
                raise event_api_exceptions.TooEarly
            elif (
                    self.action != "destroy"
                    and registration.event.last_possible_update < timezone.now()
            ):
                raise event_api_exceptions.TooLate

        return registration


class RegistrationBooleanAttributeViewSet(
    mixins.CreateModelMixin, viewsets.GenericViewSet
):
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs) -> Response:
        post_serializer = BooleanAttributePostSerializer(data=request.data)
        post_serializer.is_valid(raise_exception=True)

        attribute_module, registration = get_attribute_params(kwargs, post_serializer)

        attribute = BooleanAttribute.objects.create(
            attribute_module=attribute_module,
            registration=registration,
            boolean_field=post_serializer.data.get("boolean_field", False),
        )

        result_serializer = BooleanAttributeSerializer(attribute)
        return Response(result_serializer.data, status=status.HTTP_201_CREATED)


class RegistrationStringAttributeViewSet(
    mixins.CreateModelMixin, viewsets.GenericViewSet
):
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs) -> Response:
        post_serializer = StringAttributePostSerializer(data=request.data)
        post_serializer.is_valid(raise_exception=True)

        attribute_module, registration = get_attribute_params(kwargs, post_serializer)

        attribute = StringAttribute.objects.create(
            attribute_module=attribute_module,
            registration=registration,
            string_field=post_serializer.data.get("string_field", ""),
        )

        result_serializer = StringAttributeSerializer(attribute)
        return Response(result_serializer.data, status=status.HTTP_201_CREATED)


class RegistrationIntegerAttributeViewSet(
    mixins.CreateModelMixin, viewsets.GenericViewSet
):
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs) -> Response:
        post_serializer = IntegerAttributePostSerializer(data=request.data)
        post_serializer.is_valid(raise_exception=True)

        attribute_module, registration = get_attribute_params(kwargs, post_serializer)

        attribute = IntegerAttribute.objects.create(
            attribute_module=attribute_module,
            registration=registration,
            integer_field=post_serializer.data.get("integer_field", 0),
        )

        result_serializer = IntegerAttributeSerializer(attribute)
        return Response(result_serializer.data, status=status.HTTP_201_CREATED)


class RegistrationFloatAttributeViewSet(
    mixins.CreateModelMixin, viewsets.GenericViewSet
):
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs) -> Response:
        post_serializer = FloatAttributePostSerializer(data=request.data)
        post_serializer.is_valid(raise_exception=True)

        attribute_module, registration = get_attribute_params(kwargs, post_serializer)

        attribute = FloatAttribute.objects.create(
            attribute_module=attribute_module,
            registration=registration,
            float_field=post_serializer.data.get("float_field", 0.0),
        )

        result_serializer = FloatAttributeSerializer(attribute)
        return Response(result_serializer.data, status=status.HTTP_201_CREATED)


class RegistrationDateTimeAttributeViewSet(
    mixins.CreateModelMixin, viewsets.GenericViewSet
):
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs) -> Response:
        post_serializer = DateTimeAttributePostSerializer(data=request.data)
        post_serializer.is_valid(raise_exception=True)

        attribute_module, registration = get_attribute_params(kwargs, post_serializer)

        attribute = DateTimeAttribute.objects.create(
            attribute_module=attribute_module,
            registration=registration,
            date_time_field=post_serializer.data.get("date_time_field", None),
        )

        result_serializer = DateTimeAttributeSerializer(attribute)
        return Response(result_serializer.data, status=status.HTTP_201_CREATED)


class RegistrationTravelAttributeViewSet(
    mixins.CreateModelMixin, viewsets.GenericViewSet
):
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs) -> Response:
        post_serializer = TravelAttributePostSerializer(data=request.data)
        post_serializer.is_valid(raise_exception=True)

        attribute_module, registration = get_attribute_params(kwargs, post_serializer)

        attribute = TravelAttribute.objects.create(
            attribute_module=attribute_module,
            registration=registration,
            number_persons=post_serializer.data.get("number_persons", 0),
            type_field=post_serializer.data.get("type_field", TravelType.Train),
            date_time_field=post_serializer.data.get("date_time_field", None),
            description=post_serializer.data.get("description", ""),
        )

        result_serializer = TravelAttributeSerializer(attribute)
        return Response(result_serializer.data, status=status.HTTP_201_CREATED)


class RegistrationSummaryViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    permission_classes = [event_permissions.IsSubRegistrationResponsiblePerson]
    serializer_class = registration_serializers.RegistrationSummarySerializer

    def get_queryset(self) -> QuerySet:
        registration_id = self.kwargs.get("registration_pk", None)
        return Registration.objects.filter(id=registration_id)


class RegistrationViewSet(
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet
):
    permission_classes = [event_permissions.IsRegistrationResponsiblePerson]
    queryset = Registration.objects.all()

    def create(self, request, *args, **kwargs) -> Response:
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        event: event_models.Event = get_object_or_404(
            event_models.Event, pk=serializer.data["event"]
        )

        scout_organisation_id = serializer.data["scout_organisation"]
        err_msg = f"Element (Bund, Ring, Stamm) mit der Id {scout_organisation_id}"
        scout_organisation = custom_get_or_404(
            event_api_exceptions.SomethingNotFound(err_msg),
            basic_models.ScoutHierarchy,
            id=scout_organisation_id
        )
        registration: Registration = Registration(
            scout_organisation=scout_organisation,
            event=event,
        )

        registration.save()
        registration.responsible_persons.add(request.user)

        # event_module: QuerySet = event_models.EventModule.objects.filter(
        #     event=event.id, required=True
        # )
        # for mapper in event_module:
        #     for attribute_mapper in mapper.attributes.all():
        #         attribute = attribute_mapper.attribute
        #         new_attribute = add_event_attribute(attribute)
        #         registration.tags.add(new_attribute.id)

        json = registration_serializers.RegistrationGetSerializer(registration)
        return Response(json.data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs) -> Response:
        partial = kwargs.pop("partial", False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        tmp: Registration = serializer.save()

        # tmp.responsible_persons.add(request.user)

        serializer = registration_serializers.RegistrationGetSerializer(tmp)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def destroy(self, request, *args, **kwargs) -> Response:
        registration: Registration = self.get_object()
        participants_count = RegistrationParticipant.objects.filter(
            registration=registration.id
        ).count()
        if participants_count == 0:
            return super().destroy(request, *args, **kwargs)

        if registration.event.last_possible_update < timezone.now():
            raise event_api_exceptions.TooLate
        elif registration.event.registration_deadline < timezone.now():
            raise event_api_exceptions.TooManyParticipants

        return super().destroy(request, *args, **kwargs)

    def get_serializer_class(self):
        if self.request.method == "POST":
            return registration_serializers.RegistrationPostSerializer
        elif self.request.method == "GET":
            return registration_serializers.RegistrationGetSerializer
        elif self.request.method == "PUT":
            return registration_serializers.RegistrationPutSerializer
        elif self.request.method == "DESTROY":
            return registration_serializers.RegistrationPutSerializer


class MyRegistrationViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = registration_serializers.RegistrationSummarySerializer

    def get_queryset(self) -> QuerySet:
        return Registration.objects.filter(responsible_persons=self.request.user.id)


class RegistrationReadViewSet(mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    serializer_class = registration_serializers.RegistrationReadSerializer
    permission_classes = [event_permissions.IsSubRegistrationResponsiblePerson]

    def get_queryset(self) -> QuerySet:
        registration_id = self.kwargs.get("pk", None)
        return Registration.objects.filter(id=registration_id)


class SendConfirmationMail(mixins.CreateModelMixin, viewsets.GenericViewSet):
    permission_classes = [event_permissions.IsSubRegistrationResponsiblePerson]

    def create(self, request, *args, **kwargs):
        registration_id = self.kwargs.get("registration_pk", None)
        services.send_registration_created_mail(instance_id=registration_id)
        return Response(status=status.HTTP_201_CREATED)


class RegistrationRatingViewSet(viewsets.ModelViewSet):
    queryset = RegistrationRating.objects.all()
    serializer_class = registration_serializers.RegistrationRatingSerializer
