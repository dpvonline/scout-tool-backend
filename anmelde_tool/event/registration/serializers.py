from django.contrib.auth import get_user_model
from django.db.models import Sum
from rest_framework import serializers
from django.utils import timezone

from authentication.serializers import UserScoutHierarchySerializer
from basic import serializers as basic_serializers
from basic.models import EatHabit
from anmelde_tool.event import models as event_models
from anmelde_tool.event import serializers as event_serializers

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
    event_code = serializers.CharField()

    class Meta:
        model = event_models.Registration
        fields = ('single', 'event', 'event_code', 'scout_organisation')
        extra_kwargs = {
            "event_code": {"required": True},
            "single": {"required": True},
            "event": {"required": True},
            "scout_organisation": {"required": True}
        }


class RegistrationPutSerializer(serializers.ModelSerializer):
    class Meta:
        model = event_models.Registration
        fields = ('responsible_persons', 'is_confirmed', 'tags')
        extra_kwargs = {"responsible_persons": {
            "required": False, "allow_null": True}}


class RegistrationSummaryBookingOptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = event_models.BookingOption
        fields = ('name', 'price')


class RegistrationGetSerializer(serializers.ModelSerializer):
    responsible_persons = CurrentUserSerializer(many=True, read_only=True)
    # tags = basic_serializers.TagShortSerializer(many=True, read_only=True)
    scout_organisation = UserScoutHierarchySerializer()

    class Meta:
        model = event_models.Registration
        fields = ('id', 'scout_organisation', 'responsible_persons',)


class RegistrationSummaryParticipantSerializer(serializers.ModelSerializer):
    booking_option = RegistrationSummaryBookingOptionSerializer(
        many=False, read_only=True)

    class Meta:
        model = event_models.RegistrationParticipant
        fields = ('first_name', 'last_name', 'scout_name',
                  'deactivated', 'booking_option', 'eat_habit', 'scout_level')


class MyRegistrationGetSerializer(serializers.ModelSerializer):
    registrationparticipant_set = RegistrationSummaryParticipantSerializer(
        many=True, read_only=True)
    responsible_persons = CurrentUserSerializer(many=True, read_only=True)
    status = serializers.SerializerMethodField()
    scout_organisation = UserScoutHierarchySerializer()
    participant_count = serializers.SerializerMethodField()
    price = serializers.SerializerMethodField()
    event = event_serializers.EventRegistrationSerializer()
    # tags = serializers.SerializerMethodField()

    class Meta:
        model = event_models.Registration
        fields = (
            'id',
            'is_confirmed',
            'event',
            'scout_organisation',
            'is_accepted',
            'responsible_persons',
            'participant_count',
            'price',
            'registrationparticipant_set',
            'status',
        )

    def get_participant_count(self, registration: event_models.Registration) -> int:
        return registration.registrationparticipant_set.count()

    def get_price(self, registration: event_models.Registration) -> float:
        return registration.registrationparticipant_set.aggregate(
            sum=Sum('booking_option__price'))['sum']

    def get_status(self, obj: event_models.Registration) -> str:
        print(obj.event)

        if obj.event.registration_deadline > timezone.now():
            return 'pending'
        elif obj.event.registration_deadline <= timezone.now():
            return 'expired'
        else:
            return 'error'


class RegistrationParticipantShortSerializer(serializers.ModelSerializer):
    booking_option = RegistrationSummaryBookingOptionSerializer(
        many=False, read_only=True)
    scout_level = serializers.CharField(source='get_scout_level_display')
    eat_habit = serializers.SlugRelatedField(
        many=True,
        read_only=False,
        slug_field='name',
        queryset=EatHabit.objects.all(),
        required=False
    )

    class Meta:
        model = event_models.RegistrationParticipant
        fields = ('id', 'scout_name', 'first_name', 'last_name',
                  'scout_level', 'eat_habit', 'age', 'booking_option')


class RegistrationParticipantSerializer(serializers.ModelSerializer):
    eat_habit = serializers.SlugRelatedField(
        many=True,
        read_only=False,
        slug_field='name',
        queryset=EatHabit.objects.all(),
        required=False
    )

    class Meta:
        model = event_models.RegistrationParticipant
        fields = '__all__'


class RegistrationParticipantPutSerializer(serializers.ModelSerializer):
    avoid_manual_check = serializers.BooleanField(
        required=False, default=False)
    activate = serializers.BooleanField(required=False, default=False)
    eat_habit = serializers.SlugRelatedField(
        many=True,
        read_only=False,
        slug_field='name',
        queryset=EatHabit.objects.all(),
        required=False
    )

    class Meta:
        model = event_models.RegistrationParticipant
        exclude = (
            'deactivated',
            'generated',
            'registration',
            'needs_confirmation',
            'allow_permanently'
        )


class RegistrationParticipantGroupSerializer(serializers.Serializer):
    number = serializers.CharField(required=True)
    avoid_manual_check = serializers.BooleanField(
        required=False, default=False)


class RegistrationSummarySerializer(serializers.ModelSerializer):
    registrationparticipant_set = RegistrationSummaryParticipantSerializer(
        many=True, read_only=True)
    responsible_persons = CurrentUserSerializer(many=True, read_only=True)
    status = serializers.SerializerMethodField()
    scout_organisation = UserScoutHierarchySerializer()
    participant_count = serializers.SerializerMethodField()
    price = serializers.SerializerMethodField()
    event = event_serializers.EventRegistrationSerializer()
    # tags = serializers.SerializerMethodField()

    class Meta:
        model = event_models.Registration
        fields = (
            'id',
            'is_confirmed',
            'event',
            'scout_organisation',
            'is_accepted',
            'responsible_persons',
            'participant_count',
            'price',
            'registrationparticipant_set',
            'status',
        )

    def get_participant_count(self, registration: event_models.Registration) -> int:
        return registration.registrationparticipant_set.count()

    def get_price(self, registration: event_models.Registration) -> float:
        return registration.registrationparticipant_set.aggregate(
            sum=Sum('booking_option__price'))['sum']

    def get_status(self, obj: event_models.Registration) -> str:
        print(obj.event)

        if obj.event.registration_deadline > timezone.now():
            return 'pending'
        elif obj.event.registration_deadline <= timezone.now():
            return 'expired'
        else:
            return 'error'


class WorkshopSerializer(serializers.ModelSerializer):
    class Meta:
        model = event_models.Workshop
        fields = '__all__'


class RegistrationReadSerializer(serializers.ModelSerializer):
    responsible_persons = CurrentUserSerializer(many=True, read_only=True)
    scout_organisation = UserScoutHierarchySerializer()
    event = event_serializers.EventRegistrationSerializer()
    registrationparticipant_set = RegistrationSummaryParticipantSerializer(
        many=True, read_only=True)
    participant_count = serializers.SerializerMethodField()
    price = serializers.SerializerMethodField()

    class Meta:
        model = event_models.Registration
        fields = ('id', 'scout_organisation', 'responsible_persons', 'event',
                  'tags', 'price', 'participant_count', 'registrationparticipant_set',)

    def get_participant_count(self, registration: event_models.Registration) -> int:
        return registration.registrationparticipant_set.count()

    def get_price(self, registration: event_models.Registration) -> float:
        return registration.registrationparticipant_set.aggregate(
            sum=Sum('booking_option__price'))['sum']
