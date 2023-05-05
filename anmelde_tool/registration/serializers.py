from django.contrib.auth import get_user_model
from django.db.models import Sum
from django.utils import timezone
from rest_framework import serializers

from anmelde_tool.event import models as event_models
from anmelde_tool.event import serializers as event_serializers
from anmelde_tool.attributes.models import BooleanAttribute, StringAttribute, TimeAttribute, IntegerAttribute, \
    FloatAttribute, StringAttribute, TravelAttribute
from anmelde_tool.attributes.serializers import BooleanAttributeSerializer, StringAttributeSerializer, \
    TimeAttributeSerializer, IntegerAttributeSerializer, FloatAttributeSerializer, TravelAttributeSerializer
from anmelde_tool.registration.models import Registration, RegistrationParticipant
from authentication.serializers import UserScoutHierarchySerializer
from basic.models import EatHabit

User = get_user_model()


class CurrentUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            'id',
            'email',
            # 'userextended',
            'first_name',
            'last_name',
            # 'mobile_number',
            # 'scout_name',
            # 'scout_organisation',
            # 'dsgvo_confirmed'
        )


class RegistrationPostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Registration
        fields = ('event', 'scout_organisation')
        extra_kwargs = {
            "event": {
                "required": True
            },
            "scout_organisation": {
                "required": True
            }
        }


class RegistrationPutSerializer(serializers.ModelSerializer):
    class Meta:
        model = Registration
        fields = ('responsible_persons', 'is_confirmed', 'tags')
        extra_kwargs = {
            "responsible_persons": {
                "required": False,
                "allow_null": True
            }
        }


class RegistrationSummaryBookingOptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = event_models.BookingOption
        fields = ('name', 'price')


class RegistrationGetSerializer(serializers.ModelSerializer):
    responsible_persons = CurrentUserSerializer(many=True, read_only=True)
    scout_organisation = UserScoutHierarchySerializer()

    class Meta:
        model = Registration
        fields = ('id', 'scout_organisation', 'responsible_persons',)


class RegistrationParticipantSerializer(serializers.ModelSerializer):
    eat_habit = serializers.SlugRelatedField(
        many=True,
        read_only=False,
        slug_field='name',
        queryset=EatHabit.objects.all(),
        required=False
    )

    class Meta:
        model = RegistrationParticipant
        fields = '__all__'


class MyRegistrationGetSerializer(serializers.ModelSerializer):
    registrationparticipant_set = RegistrationParticipantSerializer(many=True, read_only=True)
    responsible_persons = CurrentUserSerializer(many=True, read_only=True)
    status = serializers.SerializerMethodField()
    scout_organisation = UserScoutHierarchySerializer()
    participant_count = serializers.SerializerMethodField()
    price = serializers.SerializerMethodField()
    event = event_serializers.EventRegistrationSerializer()

    class Meta:
        model = Registration
        fields = (
            'id',
            'scout_organisation',
            'responsible_persons',
            'event',
            'is_confirmed',
            'status'
        )

    def get_status(self, obj: Registration) -> str:
        if obj.event.registration_deadline > timezone.now():
            return 'pending'
        elif obj.event.registration_deadline <= timezone.now():
            return 'expired'
        else:
            return 'error'

    def get_participant_count(self, registration: Registration) -> int:
        return registration.registrationparticipant_set.count()

    def get_price(self, registration: Registration) -> float:
        return registration.registrationparticipant_set.aggregate(
            sum=Sum('booking_option__price'))['sum']


class RegistrationParticipantShortSerializer(serializers.ModelSerializer):
    booking_option = RegistrationSummaryBookingOptionSerializer(many=False, read_only=True)
    scout_level = serializers.CharField(source='get_scout_level_display')
    eat_habit = serializers.SlugRelatedField(
        many=True,
        read_only=False,
        slug_field='name',
        queryset=EatHabit.objects.all(),
        required=False
    )

    class Meta:
        model = RegistrationParticipant
        fields = (
            'id',
            'scout_name',
            'first_name',
            'last_name',
            'scout_level',
            'eat_habit',
            'age',
            'booking_option'
        )


class RegistrationParticipantPutSerializer(serializers.ModelSerializer):
    eat_habit = serializers.SlugRelatedField(
        many=True,
        read_only=False,
        slug_field='name',
        queryset=EatHabit.objects.all(),
        required=False
    )

    class Meta:
        model = RegistrationParticipant
        exclude = (
            'generated',
            'registration'
        )


class RegistrationParticipantGroupSerializer(serializers.Serializer):
    number = serializers.CharField(required=True)
    avoid_manual_check = serializers.BooleanField(required=False, default=False)


class RegistrationSummarySerializer(serializers.ModelSerializer):
    registrationparticipant_set = RegistrationParticipantSerializer(many=True, read_only=True)
    responsible_persons = CurrentUserSerializer(many=True, read_only=True)
    status = serializers.SerializerMethodField()
    scout_organisation = UserScoutHierarchySerializer()
    participant_count = serializers.SerializerMethodField()
    price = serializers.SerializerMethodField()
    event = event_serializers.EventRegistrationSerializer()

    class Meta:
        model = Registration
        fields = (
            'id',
            'is_confirmed',
            'event',
            'scout_organisation',
            'responsible_persons',
            'participant_count',
            'price',
            'registrationparticipant_set',
            'status',
        )

    def get_participant_count(self, registration: Registration) -> int:
        return registration.registrationparticipant_set.count()

    def get_price(self, registration: Registration) -> float:
        return registration.registrationparticipant_set.aggregate(
            sum=Sum('booking_option__price'))['sum']

    def get_status(self, obj: Registration) -> str:
        if obj.event.registration_deadline > timezone.now():
            return 'pending'
        elif obj.event.registration_deadline <= timezone.now():
            return 'expired'
        else:
            return 'error'


class RegistrationReadSerializer(serializers.ModelSerializer):
    responsible_persons = CurrentUserSerializer(many=True, read_only=True)
    scout_organisation = UserScoutHierarchySerializer()
    event = event_serializers.EventRegistrationSerializer()
    registrationparticipant_set = RegistrationParticipantSerializer(many=True, read_only=True)
    participant_count = serializers.SerializerMethodField()
    price = serializers.SerializerMethodField()
    attributes = serializers.SerializerMethodField()

    class Meta:
        model = Registration
        fields = (
            'id',
            'scout_organisation',
            'responsible_persons',
            'event',
            'price',
            'participant_count',
            'registrationparticipant_set',
            'attributes'
        )

    def get_participant_count(self, registration: Registration) -> int:
        return registration.registrationparticipant_set.count()

    def get_price(self, registration: Registration) -> float:
        return registration.registrationparticipant_set.aggregate(
            sum=Sum('booking_option__price'))['sum']

    def get_attributes(self, registration: Registration):
        boolean_attributes = BooleanAttribute.objects.filter(registration=registration)
        boolean_serializer = BooleanAttributeSerializer(boolean_attributes, many=True, read_only=True)

        string_attributes = StringAttribute.objects.filter(registration=registration)
        string_serializer = StringAttributeSerializer(string_attributes, many=True, read_only=True)

        integer_attributes = IntegerAttribute.objects.filter(registration=registration)
        integer_serializer = StringAttributeSerializer(integer_attributes, many=True, read_only=True)

        float_attributes = FloatAttribute.objects.filter(registration=registration)
        float_serializer = FloatAttributeSerializer(float_attributes, many=True, read_only=True)

        time_attributes = TimeAttribute.objects.filter(registration=registration)
        time_serializer = TimeAttributeSerializer(time_attributes, many=True, read_only=True)

        travel_attributes = TravelAttribute.objects.filter(registration=registration)
        travel_serializer = TravelAttributeSerializer(travel_attributes, many=True, read_only=True)
        return [*boolean_serializer.data, *string_serializer.data, *integer_serializer.data, *float_serializer.data,
                *time_serializer.data, *travel_serializer.data]
