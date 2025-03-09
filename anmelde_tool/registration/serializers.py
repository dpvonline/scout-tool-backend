from dateutil.relativedelta import relativedelta
from django.contrib.auth import get_user_model
from django.db.models import Sum, Count, F, Value
from django.db.models.functions import Coalesce
from django.utils import timezone
from rest_framework import serializers

from anmelde_tool.event import models as event_models
from anmelde_tool.event import serializers as event_serializers
from anmelde_tool.attributes.models import BooleanAttribute, StringAttribute, DateTimeAttribute, IntegerAttribute, \
    FloatAttribute, StringAttribute, TravelAttribute
from anmelde_tool.attributes.serializers import BooleanAttributeSerializer, StringAttributeSerializer, \
    DateTimeAttributeSerializer, IntegerAttributeSerializer, FloatAttributeSerializer, TravelAttributeSerializer
from basic import serializers as basic_serializers
from anmelde_tool.registration.models import Registration, RegistrationParticipant, RegistrationRating
from authentication.serializers import UserScoutHierarchySerializer
from basic.models import EatHabit

User = get_user_model()


class CurrentUserSerializer(serializers.ModelSerializer):
    phone_number = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'id',
            'email',
            # 'userextended',
            'first_name',
            'last_name',
            'phone_number',
            # 'scout_name',
            # 'scout_organisation',
            # 'dsgvo_confirmed'
        )

    def get_phone_number(self, obj: User):
        if hasattr(obj, 'person'):
            return obj.person.phone_number
        return ''


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
        fields = ('responsible_persons',)
        extra_kwargs = {
            "responsible_persons": {
                "required": False,
                "allow_null": True
            }
        }


class RegistrationSummaryBookingOptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = event_models.BookingOption
        fields = ('id', 'name', 'price')


class RegistrationGetSerializer(serializers.ModelSerializer):
    responsible_persons = CurrentUserSerializer(many=True, read_only=True)
    scout_organisation = UserScoutHierarchySerializer()

    class Meta:
        model = Registration
        fields = ('id', 'scout_organisation', 'responsible_persons',)


class RegistrationParticipantSerializer(serializers.ModelSerializer):
    allow_permanently = serializers.BooleanField(default=False, read_only=True)
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


class RegistrationParticipantReadSerializer(serializers.ModelSerializer):
    eat_habit = serializers.SlugRelatedField(
        many=True,
        read_only=False,
        slug_field='name',
        queryset=EatHabit.objects.all(),
        required=False
    )
    booking_option = RegistrationSummaryBookingOptionSerializer(
        many=False, read_only=True)
    zip_code = basic_serializers.ZipCodeSerializer(many=False, read_only=True)
    display_name = serializers.SerializerMethodField()
    age = serializers.SerializerMethodField()

    class Meta:
        model = RegistrationParticipant
        fields = (
            'id',
            'first_name',
            'last_name',
            'scout_name',
            'display_name',
            'address',
            'zip_code',
            'age',
            'scout_group',
            'phone_number',
            'email',
            'birthday',
            'gender',
            'get_gender_display',
            'eat_habit',
            'booking_option',
            'scout_function',
            'id_number',
            'scout_level',
        )

    def get_age(self, obj: RegistrationParticipant):
        if obj.birthday:
            return relativedelta(obj.registration.event.start_date.date(), obj.birthday.date()).years
        return None

    def get_display_name(self, obj):
        return_list = []

        if hasattr(obj, 'first_name') and obj.first_name:
            return_list.append(f"{obj.first_name}")

        if hasattr(obj, 'scout_name') and obj.scout_name:
            return_list.append(f"'{obj.scout_name}'")

        if hasattr(obj, 'last_name') and obj.last_name:
            return_list.append(f"{obj.last_name}")

        return ' '.join(return_list)


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


class RegistrationSummarySerializer(serializers.ModelSerializer):
    responsible_persons = CurrentUserSerializer(many=True, read_only=True)
    status = serializers.SerializerMethodField()
    scout_organisation = UserScoutHierarchySerializer()
    participant_count = serializers.SerializerMethodField()
    price = serializers.SerializerMethodField()
    registrationparticipant_set = serializers.SerializerMethodField()
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

    def get_registrationparticipant_set(self, registration: Registration) -> int:
        items = registration.registrationparticipant_set.all().order_by('first_name')
        return RegistrationParticipantReadSerializer(items, many=True).data

    def get_participant_count(self, registration: Registration) -> int:
        return registration.registrationparticipant_set.count()

    def get_price(self, registration: Registration) -> float:
        return registration.registrationparticipant_set.aggregate(
            sum=Sum('booking_option__price'))['sum']

    def get_status(self, obj: Registration) -> str:
        if obj.event.end_date > timezone.now():
            return 'pending'
        elif obj.event.end_date <= timezone.now():
            return 'expired'
        else:
            return 'error'


class RegistrationReadSerializer(serializers.ModelSerializer):
    responsible_persons = CurrentUserSerializer(many=True, read_only=True)
    scout_organisation = UserScoutHierarchySerializer()
    event = event_serializers.EventReadSerializer()
    participant_count = serializers.SerializerMethodField()
    price = serializers.SerializerMethodField()
    attributes = serializers.SerializerMethodField()
    summary = serializers.SerializerMethodField()
    registrationparticipant_set = serializers.SerializerMethodField()

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
            'attributes',
            'summary'
        )

    def get_registrationparticipant_set(self, registration: Registration) -> int:
        items = registration.registrationparticipant_set.all().order_by('first_name')
        return RegistrationParticipantReadSerializer(items, many=True).data

    def get_participant_count(self, registration: Registration) -> int:
        return registration.registrationparticipant_set.count()

    def get_price(self, registration: Registration) -> float:
        return registration.registrationparticipant_set.aggregate(
            sum=Sum('booking_option__price'))['sum']

    def get_attributes(self, registration: Registration):
        boolean_attributes = BooleanAttribute.objects.filter(
            registration=registration)
        boolean_serializer = BooleanAttributeSerializer(
            boolean_attributes, many=True, read_only=True)

        string_attributes = StringAttribute.objects.filter(
            registration=registration)
        string_serializer = StringAttributeSerializer(
            string_attributes, many=True, read_only=True)

        integer_attributes = IntegerAttribute.objects.filter(
            registration=registration)
        integer_serializer = IntegerAttributeSerializer(
            integer_attributes, many=True, read_only=True)

        float_attributes = FloatAttribute.objects.filter(
            registration=registration)
        float_serializer = FloatAttributeSerializer(
            float_attributes, many=True, read_only=True)

        time_attributes = DateTimeAttribute.objects.filter(
            registration=registration)
        time_serializer = DateTimeAttributeSerializer(
            time_attributes, many=True, read_only=True)

        travel_attributes = TravelAttribute.objects.filter(
            registration=registration)
        travel_serializer = TravelAttributeSerializer(
            travel_attributes, many=True, read_only=True)
        return [*boolean_serializer.data, *string_serializer.data, *integer_serializer.data, *float_serializer.data,
                *time_serializer.data, *travel_serializer.data]

    def get_summary(self, registration: Registration) -> dict:
        return {
            "eat_habits": registration.registrationparticipant_set.values(
                eat_habits=Coalesce(F("eat_habit__name"), Value("Ohne Essgewohnheit"))
            )
            .annotate(sum=Count("*"))
            .order_by('-sum'),

            "booking_options": registration.registrationparticipant_set.values(
                booking_options=F("booking_option__name")
            )
            .annotate(sum=Count("booking_option__name"))
            .annotate(price=Sum("booking_option__price")),

            "genders": registration.registrationparticipant_set.values(
                genders=F("gender")
            )
            .annotate(sum=Count("gender"))
        }


class RegistrationRatingSerializer(serializers.ModelSerializer):
    class Meta:
        model = RegistrationRating
        fields = '__all__'
