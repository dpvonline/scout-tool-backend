from dateutil.relativedelta import relativedelta
from django.contrib.auth import get_user_model
from django.db.models import Sum, Count, F, QuerySet, Q
from django.utils import timezone
from rest_framework import serializers
import uuid

from anmelde_tool.attributes.models import (
    AttributeModule,
    DateTimeAttribute,
    BooleanAttribute,
    IntegerAttribute,
    FloatAttribute,
    StringAttribute,
    TravelAttribute,
    AbstractAttribute
)
from anmelde_tool.event import models as event_models
from anmelde_tool.event import serializers as event_serializer
from anmelde_tool.event import permissions as event_permissions
from anmelde_tool.event.cash import serializers as cash_serializers
from anmelde_tool.event.helper import get_bund_or_ring
from anmelde_tool.registration import serializers as registration_serializers
from anmelde_tool.registration.models import Registration, RegistrationParticipant
from anmelde_tool.registration.serializers import RegistrationGetSerializer
from anmelde_tool.workshop.models import Workshop
from basic import serializers as basic_serializers
from basic.models import EatHabit

User = get_user_model()


class WorkshopEventSummarySerializer(serializers.ModelSerializer):
    supervisor = registration_serializers.CurrentUserSerializer(
        many=False, read_only=True
    )
    type = serializers.CharField(source="get_type_display")

    class Meta:
        model = Workshop
        fields = "__all__"


class RegistrationEventSummarySerializer(serializers.ModelSerializer):
    responsible_persons = serializers.SlugRelatedField(
        many=True, read_only=True, slug_field="email"
    )
    participant_count = serializers.SerializerMethodField()
    price = serializers.SerializerMethodField()
    scout_organisation = basic_serializers.ScoutHierarchyDetailedSerializer(
        many=False, read_only=True
    )
    booking_options = serializers.SerializerMethodField()
    responsible_persons_extended = serializers.SerializerMethodField()
    scout_organisation_display = serializers.SerializerMethodField()

    class Meta:
        model = Registration
        fields = (
            "id",
            "is_confirmed",
            "scout_organisation",
            "responsible_persons",
            "responsible_persons_extended",
            "participant_count",
            "price",
            "created_at",
            "updated_at",
            "booking_options",
            "scout_organisation_display",
        )

    def get_participant_count(self, registration: Registration) -> int:
        booking_option_list = self.context["request"].query_params.getlist(
            "booking-option"
        )
        queryset = registration.registrationparticipant_set

        if booking_option_list:
            queryset = queryset.filter(booking_option__in=booking_option_list)

        return queryset.count()

    def get_price(self, registration: Registration) -> float:
        booking_option_list = self.context["request"].query_params.getlist(
            "booking-option"
        )
        queryset = registration.registrationparticipant_set

        if booking_option_list:
            queryset = queryset.filter(booking_option__in=booking_option_list)

        return queryset.aggregate(sum=Sum("booking_option__price"))["sum"]

    def get_booking_options(self, registration: Registration) -> dict:
        return (
            registration.registrationparticipant_set.values(
                booking_options=F("booking_option__name")
            )
            .annotate(sum=Count("booking_option__name"))
            .annotate(price=Sum("booking_option__price"))
        )

    def get_responsible_persons_extended(self, registration: Registration) -> str:
        return_string = ""
        for person in registration.responsible_persons.all():
            return_string = return_string + f"{person.first_name} "
        return return_string

    def get_scout_organisation_display(self, registration: Registration) -> str:
        return_string = ""
        scout_organisation = registration.scout_organisation
        if scout_organisation:
            return_string = f"{scout_organisation.name}"
        return return_string


class RegistrationParticipantEventDetailedSummarySerializer(
    serializers.ModelSerializer
):
    booking_option = (
        registration_serializers.RegistrationSummaryBookingOptionSerializer(
            many=False, read_only=True
        )
    )
    scout_group = basic_serializers.ScoutHierarchyDetailedSerializer(
        many=False, read_only=True
    )
    gender = serializers.CharField(source="get_gender_display")
    leader = serializers.CharField(source="get_leader_display")
    zip_code = basic_serializers.ZipCodeSerializer(many=False, read_only=True)
    eat_habit = serializers.SlugRelatedField(
        many=True,
        read_only=False,
        slug_field="name",
        queryset=EatHabit.objects.all(),
        required=False,
    )
    age = serializers.SerializerMethodField()
    reg_id = serializers.SerializerMethodField()

    class Meta:
        model = RegistrationParticipant
        exclude = (
            "registration",
            "id",
        )

    def get_reg_id(self, participant: RegistrationParticipant) -> uuid.UUID:
        return participant.registration.id

    def get_age(self, participant: RegistrationParticipant) -> str:
        return relativedelta(timezone.now(), participant.birthday).years


class RegistrationLocationSerializer(serializers.ModelSerializer):
    participant_count = serializers.SerializerMethodField()
    scout_organisation = basic_serializers.ScoutHierarchyDetailedSerializer(
        many=False, read_only=True
    )

    class Meta:
        model = Registration
        fields = (
            "scout_organisation",
            "participant_count",
            "created_at",
            "updated_at",
        )

    def get_participant_count(self, registration: Registration) -> int:
        booking_option_list = self.context["request"].query_params.getlist(
            "booking-option"
        )
        queryset = registration.registrationparticipant_set

        if booking_option_list:
            queryset = queryset.filter(booking_option__in=booking_option_list)

        return queryset.count()


class EventLocationSummarySerializer(serializers.ModelSerializer):
    location = event_serializer.EventLocationSummarySerializer(
        many=False, read_only=True
    )

    class Meta:
        model = event_models.Event
        fields = ("location",)


class RegistrationAttributeGetSerializer(serializers.ModelSerializer):
    scout_organisation = basic_serializers.NameOnlyScoutHierarchySerializer(
        many=False, read_only=True
    )
    responsible_persons = registration_serializers.CurrentUserSerializer(
        many=True, read_only=True
    )

    class Meta:
        model = Registration
        fields = ("scout_organisation", "is_confirmed", "responsible_persons")


class RegistrationCashSummarySerializer(serializers.ModelSerializer):
    responsible_persons = registration_serializers.CurrentUserSerializer(
        many=True, read_only=True
    )
    participant_count = serializers.SerializerMethodField()
    payment = serializers.SerializerMethodField()
    scout_organisation = basic_serializers.ScoutHierarchyDetailedSerializer(
        many=False, read_only=True
    )
    booking_options = serializers.SerializerMethodField()
    cashincome_set = cash_serializers.CashIncomeReadSerializer(
        many=True, read_only=True
    )
    ref_id = serializers.SerializerMethodField()

    class Meta:
        model = Registration
        fields = (
            "id",
            "is_confirmed",
            "scout_organisation",
            "responsible_persons",
            "participant_count",
            "payment",
            "created_at",
            "updated_at",
            "booking_options",
            "cashincome_set",
            "ref_id",
        )

    def get_participant_count(self, registration: Registration) -> int:
        return registration.registrationparticipant_set.count()

    def get_payment(self, registration: Registration) -> dict:
        total_price = (
            registration.registrationparticipant_set.aggregate(
                sum=Sum("booking_option__price")
            )["sum"]
            or 0
        )
        paid = registration.cashincome_set.aggregate(sum=Sum("amount"))["sum"] or 0.0
        difference = float(total_price) - paid

        return {
            "price": total_price,
            "paid": paid,
            "open": difference,
        }

    def get_booking_options(self, registration: Registration) -> dict:
        return (
            registration.registrationparticipant_set.values(
                booking_options=F("booking_option__name")
            )
            .annotate(sum=Count("booking_option__name"))
            .annotate(price=Sum("booking_option__price"))
        )

    def get_ref_id(self, registration: Registration) -> str:
        return (
            f'{registration.event.name.replace(" ", "")[:10]}'
            f'-{registration.scout_organisation.name.replace(" ", "")[:10]}'
            f"-{str(registration.created_at.timestamp())[:10]}"
        )


class CashSummarySerializer(serializers.ModelSerializer):
    class Meta:
        model = Registration
        fields = "__all__"


class UserEmailSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("email",)


class BooleanAttributeSummarySerializer(serializers.ModelSerializer):
    type = serializers.ReadOnlyField(default="booleanAttribute")
    registration = RegistrationGetSerializer(many=False, read_only=True)

    class Meta:
        model = BooleanAttribute
        fields = "__all__"


class DateTimeAttributeSummarySerializer(serializers.ModelSerializer):
    type = serializers.ReadOnlyField(default="dateTimeAttribute")
    registration = RegistrationGetSerializer(many=False, read_only=True)

    class Meta:
        model = DateTimeAttribute
        fields = "__all__"


class IntegerAttributeSummarySerializer(serializers.ModelSerializer):
    type = serializers.ReadOnlyField(default="integerAttribute")
    registration = RegistrationGetSerializer(many=False, read_only=True)

    class Meta:
        model = IntegerAttribute
        fields = "__all__"


class FloatAttributeSummarySerializer(serializers.ModelSerializer):
    type = serializers.ReadOnlyField(default="floatAttribute")
    registration = RegistrationGetSerializer(many=False, read_only=True)

    class Meta:
        model = FloatAttribute
        fields = "__all__"


class StringAttributeSummarySerializer(serializers.ModelSerializer):
    type = serializers.ReadOnlyField(default="stringAttribute")
    registration = RegistrationGetSerializer(many=False, read_only=True)

    class Meta:
        model = StringAttribute
        fields = "__all__"


class TravelAttributeSummarySerializer(serializers.ModelSerializer):
    type = serializers.ReadOnlyField(default="travelAttribute")
    registration = RegistrationGetSerializer(many=False, read_only=True)
    type_field = serializers.CharField(source="get_type_field_display", read_only=True)

    class Meta:
        model = TravelAttribute
        fields = "__all__"


class AttributeSummarySerializer(serializers.ModelSerializer):
    field_type = serializers.CharField(source="get_field_type_display", read_only=True)
    attribute_set = serializers.SerializerMethodField()

    class Meta:
        model = AttributeModule
        fields = (
            "id",
            "title",
            "text",
            "field_type",
            "attribute_set",
        )

    def filter_attributes_by_leadership(self,
                                        request,
                                        event: event_models.Event,
                                        attributes: QuerySet[AbstractAttribute]
                                        ) -> QuerySet[AbstractAttribute]:
        user = request.user
        leader_ship = event_permissions.check_leader_permission(event, user)
        event_role = event_permissions.check_event_permission(event, request)
        if event_role == event_permissions.EventRole.NONE and leader_ship != event_permissions.LeadershipRole.NONE:
            scout_orga = get_bund_or_ring(
                user.person.scout_group,
                leader_ship == event_permissions.LeadershipRole.BUND_LEADER
            )

            if not scout_orga:
                return BooleanAttribute.objects.none()

            attributes = attributes.filter(
                Q(registration__scout_organisation=scout_orga)
                | Q(registration__scout_organisation__parent=scout_orga)
                | Q(registration__scout_organisation__parent__parent=scout_orga)
                | Q(registration__scout_organisation__parent__parent__parent=scout_orga))
        return attributes

    def get_attribute_set(self, attribute_module: AttributeModule) -> []:
        request = self.context['request']
        if attribute_module.event_module and attribute_module.event_module.event:
            event = attribute_module.event_module.event
        elif (request.parser_context
              and request.parser_context.get("kwargs")
              and request.parser_context["kwargs"].get("event_pk")):
            event = request.parser_context["kwargs"]["event_pk"]
        else:
            return []

        if attribute_module.field_type == "BoA":
            items = BooleanAttribute.objects.filter(attribute_module=attribute_module)
            items = self.filter_attributes_by_leadership(request, event, items)
            return BooleanAttributeSummarySerializer(items, many=True, read_only=True).data
        elif attribute_module.field_type == "TiA":
            items = DateTimeAttribute.objects.filter(attribute_module=attribute_module)
            items = self.filter_attributes_by_leadership(request, event, items)
            return DateTimeAttributeSummarySerializer(items, many=True, read_only=True).data
        elif attribute_module.field_type == "InA":
            items = IntegerAttribute.objects.filter(attribute_module=attribute_module)
            items = self.filter_attributes_by_leadership(request, event, items)
            return IntegerAttributeSummarySerializer(items, many=True, read_only=True).data
        elif attribute_module.field_type == "FlA":
            items = FloatAttribute.objects.filter(attribute_module=attribute_module)
            items = self.filter_attributes_by_leadership(request, event, items)
            return FloatAttributeSummarySerializer(items, many=True, read_only=True).data
        elif attribute_module.field_type == "StA":
            items = StringAttribute.objects.filter(attribute_module=attribute_module)
            items = self.filter_attributes_by_leadership(request, event, items)
            return StringAttributeSummarySerializer(items, many=True, read_only=True).data
        elif attribute_module.field_type == "TrA":
            items = TravelAttribute.objects.filter(attribute_module=attribute_module)
            items = self.filter_attributes_by_leadership(request, event, items)
            return TravelAttributeSummarySerializer(items, many=True, read_only=True).data


class EventModuleSummarySerializer(serializers.ModelSerializer):
    attribute_modules = serializers.SerializerMethodField()

    class Meta:
        model = event_models.EventModule
        fields = ("id", "name", "header", "description", "attribute_modules")

    def get_attribute_modules(self, module: event_models.EventModule):
        queryset = module.attributemodule_set
        result = AttributeSummarySerializer(queryset, many=True, context={'request': self.context['request']}).data
        return result
