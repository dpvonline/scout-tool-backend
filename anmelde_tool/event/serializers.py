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
        fields = ('id',
                  'name',
                  'short_description',
                  'long_description',
                  'location',
                  'start_date',
                  'end_date',
                  'registration_deadline',
                  'registration_start',
                  'last_possible_update',
                  'tags',
                  'cloud_link',
                  'personal_data_required')


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


class EventCompleteSerializer(serializers.ModelSerializer):
    status = serializers.SerializerMethodField()
    responsible_persons = serializers.SlugRelatedField(
        many=True,
        read_only=False,
        slug_field='email',
        queryset=User.objects.all()
    )

    event_planer_modules = serializers.SlugRelatedField(
        many=True,
        read_only=False,
        slug_field='name',
        queryset=event_models.EventPlanerModule.objects.all()
    )

    class Meta:
        model = event_models.Event
        fields = '__all__'
        
    def get_status(self, obj: event_models.EventLocation) -> str:
        registration = event_models.Registration.objects.filter(event=obj.id).filter(responsible_persons=self.context['request'].user).first()
        print(registration)
        
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
        fields = ('name', 'zip_code', 'address', 'distance')
        
    def get_distance(self, obj: event_models.EventLocation) -> float:
        person = auth_models.Person.objects.filter(user=self.context['request'].user).first()

        coords_1 = (obj.zip_code.lat, obj.zip_code.lon)
        coords_2 = (person.zip_code.lat, person.zip_code.lon)

        return geopy.distance.geodesic(coords_1, coords_2).km


class EventPlanerModuleSerializer(serializers.ModelSerializer):
    class Meta:
        model = event_models.EventPlanerModule
        fields = '__all__'


class EventReadSerializer(serializers.ModelSerializer):
    tags = basic_serializers.TagShortSerializer(many=True)
    location = EventLocationShortSerializer(many=False, read_only=True)
    # eventmodulemapper_set = EventModuleMapperGetSerializer(many=True, read_only=True)
    event_planer_modules = EventPlanerModuleSerializer(many=True, read_only=True)
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
    registration_options = serializers.SerializerMethodField()
    location = EventLocationShortSerializer(read_only=True, many=False)
    allow_statistic = serializers.SerializerMethodField()
    is_confirmed = serializers.SerializerMethodField()
    allow_statistic_admin = serializers.SerializerMethodField()
    allow_statistic_leader = serializers.SerializerMethodField()
    single_registration_level = basic_serializers.ScoutOrgaLevelSerializer(many=False, read_only=True)
    group_registration_level = basic_serializers.ScoutOrgaLevelSerializer(many=False, read_only=True)

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
            'tags',
            'registration_options',
            'allow_statistic',
            'allow_statistic_admin',
            'allow_statistic_leader',
            'is_confirmed',
            'icon',
            'theme',
            'single_registration_level',
            'group_registration_level'
        )

    def get_allow_statistic(self, obj: event_models.Event) -> bool:
        return event_permissions.check_event_permission(obj, self.context['request'].user)

    def get_allow_statistic_leader(self, obj: event_models.Event) -> bool:
        return event_permissions.check_leader_permission(obj, self.context['request'].user)

    def get_allow_statistic_admin(self, obj: event_models.Event) -> bool:
        return event_permissions.check_event_permission_admin(obj, self.context['request'].user)

    def get_can_register(self, obj: event_models.Event) -> bool:
        return obj.registration_deadline > timezone.now() >= obj.registration_start

    def get_can_edit(self, obj: event_models.Event) -> bool:
        return obj.last_possible_update >= timezone.now()

    def get_is_confirmed(self, obj: event_models.Event) -> bool:
        user: User = self.context['request'].user
        reg: QuerySet[event_models.Registration] = obj.registration_set. \
            filter(responsible_persons__in=[user.id])
        if reg.first():
            return reg.first().is_confirmed
        return False

    @staticmethod
    def match_registration_allowed_level(user: User, registration_level: int) -> bool:
        # ToDo: Hagi fix it
        # if registration_level == 6:
        #     return user.userextended.scout_organisation.level.id in {5, 6}
        # elif registration_level in {2, 3, 4, 5}:
        #     return user.userextended.scout_organisation.level.id >= registration_level
        return False

    def get_registration_options(self, obj: event_models.Event) -> dict:
        user = self.context['request'].user

        group_id = None
        single_id = None
        allow_edit_group_reg = False
        allow_edit_single_reg = False

        # ToDo: Hagi fix it
        # user_orga = user.userextended.scout_organisation
        # orga_filter = Q(scout_organisation=user_orga)

        # if user_orga.parent:
        #     orga_filter |= Q(scout_organisation=user_orga.parent)
        #     if user_orga.parent.parent:
        #         orga_filter |= Q(scout_organisation=user_orga.parent.parent)

        # existing_group: QuerySet = obj.registration_set. \
        #     filter(orga_filter, single=False)
        # group: QuerySet[event_models.Registration] = existing_group. \
        #     filter(responsible_persons__in=[user.id])
        # single: QuerySet[event_models.Registration] = obj.registration_set. \
        #     filter(responsible_persons__in=[user.id], single=True)

        # if existing_group.exists():
        #     group_id = existing_group.first().id
        #     allow_edit_group_reg = group.exists() and existing_group.exists() and self.get_can_edit(obj)

        # if single.exists():
        #     single_id = single.first().id
        #     allow_edit_single_reg = self.get_can_edit(obj) and not allow_edit_group_reg

        allow_new_group_reg = not group_id \
                              and not single_id \
                              and self.match_registration_allowed_level(user, obj.group_registration_level.id) \
                              and self.get_can_register(obj) \
                              and obj.group_registration != event_choices.RegistrationTypeGroup.No
        allow_new_single_reg = not single_id \
                               and not allow_edit_group_reg \
                               and self.match_registration_allowed_level(user, obj.single_registration_level.id) \
                               and self.get_can_register(obj) \
                               and obj.single_registration != event_choices.RegistrationTypeGroup.No

        return {
            'group_id': group_id,
            'allow_new_group_reg': allow_new_group_reg,
            'allow_edit_group_reg': allow_edit_group_reg,
            'single_id': single_id,
            'allow_new_single_reg': allow_new_single_reg,
            'allow_edit_single_reg': allow_edit_single_reg
        }
