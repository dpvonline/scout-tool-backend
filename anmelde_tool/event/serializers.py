import geopy.distance
from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework import serializers

from anmelde_tool.attributes.serializers import AttributeModuleEventReadSerializer
from anmelde_tool.email_services import serializers as email_services_serializers
from anmelde_tool.event import models as event_models
from anmelde_tool.event import permissions as event_permissions
from anmelde_tool.event.models import EventModule
from anmelde_tool.registration.models import Registration
from authentication.serializers import UserScoutHierarchySerializer
from basic import serializers as basic_serializers
from keycloak_auth import serializers as keycloak_serializers

User = get_user_model()


class EventLocationSummarySerializer(serializers.ModelSerializer):
    zip_code = basic_serializers.ZipCodeSerializer(many=False, read_only=True)

    class Meta:
        model = event_models.EventLocation
        fields = '__all__'


class EventLocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = event_models.EventLocation
        fields = '__all__'


class EventLocationShortSerializer(serializers.ModelSerializer):
    distance = serializers.SerializerMethodField()
    zip_code = basic_serializers.ZipCodeShortSerializer(many=False, read_only=True)

    class Meta:
        model = event_models.EventLocation
        fields = (
            'name',
            'zip_code',
            'address',
            'distance'
        )

    def get_distance(self, obj: event_models.EventLocation) -> float:
        person = self.context['request'].user.person
        if not person.zip_code:
            return None
        coords_1 = (obj.zip_code.lat, obj.zip_code.lon)
        coords_2 = (person.zip_code.lat, person.zip_code.lon)

        return geopy.distance.geodesic(coords_1, coords_2).km


class EventRegistrationSerializer(serializers.ModelSerializer):
    class Meta:
        model = event_models.Event
        fields = (
            'id',
            'name',
            'short_description',
            'long_description',
            'location',
            'start_date',
            'end_date',
            'registration_deadline',
            'registration_start',
            'last_possible_update',
            'cloud_link',
        )


class BookingOptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = event_models.BookingOption
        fields = '__all__'


class EventModuleSerializer(serializers.ModelSerializer):
    class Meta:
        model = event_models.EventModule
        fields = '__all__'


class EventPostSerializer(serializers.ModelSerializer):
    price = serializers.FloatField(required=False)
    responsible_persons = serializers.SlugRelatedField(
        many=True,
        read_only=False,
        slug_field='email',
        queryset=User.objects.all()
    )

    class Meta:
        model = event_models.Event
        fields = '__all__'
        extra_kwargs = {
            'start_date': {'required': True},
            'end_date': {'required': True},
            'registration_deadline': {'required': True},
            'registration_start': {'required': True},
        }


class EventCompleteSerializer(serializers.ModelSerializer):
    status = serializers.SerializerMethodField()
    responsible_persons = serializers.SlugRelatedField(
        many=True,
        read_only=False,
        slug_field='email',
        queryset=User.objects.all()
    )

    class Meta:
        model = event_models.Event
        fields = '__all__'

    def get_status(self, obj: event_models.Event) -> str:
        registration = Registration.objects \
            .filter(event=obj.id, responsible_persons=self.context['request'].user) \
            .exists()

        if registration:
            return 'already'
        elif obj.registration_deadline > timezone.now():
            return 'pending'
        elif obj.registration_deadline <= timezone.now():
            return 'expired'
        else:
            return 'error'


class EventReadModuleSerializer(serializers.ModelSerializer):
    attribute_modules = serializers.SerializerMethodField()

    class Meta:
        model = EventModule
        fields = (
            'name',
            'description',
            'header',
            'ordering',
            'required',
            'attribute_modules'
        )

    def get_attribute_modules(self, instance: EventModule):
        queryset = instance.attributemodule_set.all()
        serializer = AttributeModuleEventReadSerializer(queryset, many=True, read_only=True)
        return serializer.data


class EventReadSerializer(serializers.ModelSerializer):
    location = EventLocationShortSerializer(many=False, read_only=True)
    eventmodule_set = EventReadModuleSerializer(many=True, read_only=True)
    status = serializers.SerializerMethodField()
    admin_group = keycloak_serializers.GroupShortSerializer(many=False, read_only=True)
    view_group = keycloak_serializers.GroupShortSerializer(many=False, read_only=True)
    invited_groups = keycloak_serializers.GroupShortSerializer(many=True, read_only=True)
    email_set = email_services_serializers.StandardEmailRegistrationSetSerializer(many=False, read_only=True)
    inviting_group = keycloak_serializers.GroupShortSerializer(many=False, read_only=True)
    limited_registration_hierarchy = UserScoutHierarchySerializer(many=False, read_only=True)
    responsible_persons = serializers.SlugRelatedField(
        many=True,
        read_only=False,
        slug_field='email',
        queryset=User.objects.all()
    )
    registration_level = basic_serializers.ScoutOrgaLevelSerializer(many=False, read_only=True)
    theme = basic_serializers.FrontendThemeSerializer(many=False, read_only=True)
    booking_options = serializers.SerializerMethodField()

    class Meta:
        model = event_models.Event
        fields = '__all__'

    def get_status(self, obj: event_models.Event) -> str:

        if obj.registration_deadline > timezone.now():
            return 'pending'
        elif obj.registration_deadline <= timezone.now():
            return 'expired'
        else:
            return 'error'

    def get_booking_options(self, obj: event_models.Event) -> list:
        booking_options = event_models.BookingOption.objects.filter(event=obj.id)
        return BookingOptionSerializer(booking_options, many=True).data


class EventOverviewSerializer(serializers.ModelSerializer):
    status = serializers.SerializerMethodField()
    location = EventLocationShortSerializer(read_only=True, many=False)
    can_view = serializers.SerializerMethodField()
    can_view_leader = serializers.SerializerMethodField()
    can_edit = serializers.SerializerMethodField()

    class Meta:
        model = event_models.Event
        fields = '__all__'

    def get_can_view(self, obj: event_models.Event) -> bool:
        return event_permissions.check_event_permission(obj, self.context['request'])

    def get_can_view_leader(self, obj: event_models.Event) -> bool:
        return event_permissions.check_leader_permission(obj, self.context['request'].user)

    def get_can_edit(self, obj: event_models.Event) -> bool:
        return event_permissions.check_event_permission(obj, self.context['request'], admin_only=True)

    def get_status(self, obj: event_models.Event) -> str:

        if obj.end_date > timezone.now() and obj.is_public:
            return 'open'
        elif obj.end_date > timezone.now() and not obj.is_public:
            return 'wip'
        elif obj.end_date <= timezone.now():
            return 'closed'
        else:
            return 'error'


class MyInvitationsSerializer(serializers.ModelSerializer):
    status = serializers.SerializerMethodField()
    booking_options = serializers.SerializerMethodField()
    location = EventLocationShortSerializer(many=False, read_only=True)

    class Meta:
        model = event_models.Event
        fields = (
            'id',
            'created_at',
            'updated_at',
            'status',
            'name',
            'short_description',
            'long_description',
            'icon',
            'location',
            'start_date',
            'end_date',
            'registration_deadline',
            'registration_start',
            'last_possible_update',
            'booking_options',
        )

    def get_status(self, obj: event_models.Event) -> str:
        registration = Registration.objects \
            .filter(event=obj.id, responsible_persons=self.context['request'].user) \
            .exists()

        if registration:
            return 'already'
        elif obj.registration_deadline > timezone.now():
            return 'pending'
        elif obj.registration_deadline <= timezone.now():
            return 'expired'
        else:
            return 'error'

    def get_booking_options(self, obj: event_models.Event) -> list:
        booking_options = event_models.BookingOption.objects.filter(event=obj.id)
        return BookingOptionSerializer(booking_options, many=True).data
