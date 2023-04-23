from django.contrib.auth import get_user_model
from django.db.models import QuerySet, Q
from django.utils import timezone
from rest_framework import serializers
from authentication import models as auth_models
import geopy.distance
from datetime import datetime

from anmelde_tool.attributes.serializers import AbstractAttributeGetPolymorphicSerializer
from authentication.serializers import UserScoutHierarchySerializer
from basic import serializers as basic_serializers
from authentication import serializers as auth_serializers
from anmelde_tool.event import models as event_models
from anmelde_tool.event import permissions as event_permissions
from anmelde_tool.event.choices import choices as event_choices

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


class EventModuleShortSerializer(serializers.ModelSerializer):
    class Meta:
        model = event_models.EventModule
        fields = ('header', 'name')


class EventModuleMapperShortSerializer(serializers.ModelSerializer):
    module = EventModuleShortSerializer(read_only=True)

    class Meta:
        model = event_models.EventModuleMapper
        fields = ('ordering', 'module', 'required')


class EventModuleMapperGetSerializer(serializers.ModelSerializer):
    module = EventModuleSerializer(read_only=True)

    # attributes = AbstractAttributeGetPolymorphicSerializer(read_only=True, many=True)

    class Meta:
        model = event_models.EventModuleMapper
        fields = '__all__'


class EventModuleMapperSerializer(serializers.ModelSerializer):
    class Meta:
        model = event_models.EventModuleMapper
        fields = '__all__'


class EventModuleMapperPostSerializer(serializers.ModelSerializer):
    class Meta:
        model = event_models.EventModuleMapper
        fields = (
            'attributes',
            'event',
            'overwrite_description',
            'ordering'
        )
        optional_fields = ('module',)


class EventModuleMapperPutSerializer(serializers.ModelSerializer):
    class Meta:
        model = event_models.EventModuleMapper
        fields = (
            'attributes',
            'overwrite_description',
            'ordering'
        )


class EventPostSerializer(serializers.ModelSerializer):
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
        registration = event_models.Registration.objects.filter(event=obj.id).filter(
            responsible_persons=self.context['request'].user).first()

        if registration:
            return 'already'
        elif obj.registration_deadline > timezone.now():
            return 'pending'
        elif obj.registration_deadline <= timezone.now():
            return 'expired'
        else:
            return 'error'


class EventPlanerSerializer(serializers.ModelSerializer):
    tags = basic_serializers.TagShortSerializer(many=True)

    # eventmodulemapper_set = EventModuleMapperGetSerializer(many=True, read_only=True)

    class Meta:
        model = event_models.Event
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


class EventReadSerializer(serializers.ModelSerializer):
    tags = basic_serializers.TagShortSerializer(many=True)
    location = EventLocationShortSerializer(many=False, read_only=True)
    # eventmodulemapper_set = EventModuleMapperGetSerializer(many=True, read_only=True)
    keycloak_path = auth_serializers.GroupSerializer(many=False, read_only=True)
    limited_registration_hierarchy = UserScoutHierarchySerializer(many=False, read_only=True)

    class Meta:
        model = event_models.Event
        fields = '__all__'


class AttributeEventModuleMapperSerializer(serializers.ModelSerializer):
    attribute = AbstractAttributeGetPolymorphicSerializer(many=False, read_only=False)

    class Meta:
        model = event_models.AttributeEventModuleMapper
        fields = '__all__'


class AttributeEventModuleMapperPostSerializer(serializers.ModelSerializer):
    class Meta:
        model = event_models.AttributeEventModuleMapper
        fields = '__all__'


class EventOverviewSerializer(serializers.ModelSerializer):
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
        return event_permissions.check_leader_permission(obj, self.context['request'])

    def get_can_edit(self, obj: event_models.Event) -> bool:
        return event_permissions.check_event_permission(obj, self.context['request'], admin_only=True)


class MyInvitationsSerializer(serializers.ModelSerializer):
    status = serializers.SerializerMethodField()
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
            'last_possible_update'
        )

    def get_status(self, obj: event_models.Event) -> str:
        registration = event_models.Registration.objects.filter(event=obj.id).filter(
            responsible_persons=self.context['request'].user).first()

        if registration:
            return 'already'
        elif obj.registration_deadline > timezone.now():
            return 'pending'
        elif obj.registration_deadline <= timezone.now():
            return 'expired'
        else:
            return 'error'
