from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.core.validators import EmailValidator
from rest_framework import serializers

from anmelde_tool.event.choices.choices import ScoutLevelTypes, LeaderTypes
from authentication.choices import BundesPostTextChoice, EmailNotificationType
from authentication.models import CustomUser, Person, RequestGroupAccess
from basic.choices import Gender
from basic.models import ScoutHierarchy
from basic.serializers import ZipCodeDetailedSerializer, EatHabitSerializer, ScoutHierarchyDetailedSerializer
from keycloak_auth.models import KeycloakGroup

User: CustomUser = get_user_model()


class UserScoutHierarchySerializer(serializers.ModelSerializer):
    """
    Serializer of the ScoutHierarchy model as extension for the UserExtended serializers
    including a serializer for `bund` where the name is picked up by iterating through the parents
    """
    bund = serializers.SerializerMethodField()

    class Meta:
        model = ScoutHierarchy
        fields = ('id', 'name', 'parent', 'zip_code', 'bund')

    @staticmethod
    def get_bund(obj: ScoutHierarchy) -> str:
        """
        @param obj: model instance
        @return: name of `bund` as string
        searches in the ScoutHierarchy for the parent having the level `Bund` and returns the filtered name
        """
        iterator: ScoutHierarchy = obj
        while iterator is not None:
            if iterator.level.name == 'Bund':
                return iterator.name
            iterator = iterator.parent


class UserShortSerializer(serializers.ModelSerializer):
    """
    Serializer for the User model containing only name and mobile number
    """
    scout_name = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'mobile_number',
            'scout_name',
        )

    def get_scout_name(self, user: CustomUser) -> str:
        return user.person.scout_name


class UserRequestSerializer(serializers.ModelSerializer):
    scout_group = serializers.SerializerMethodField()
    scout_name = serializers.SerializerMethodField()
    first_name = serializers.SerializerMethodField()
    last_name = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'email',
            'username',
            'scout_name',
            'scout_group',
            'first_name',
            'last_name'
        )

    def get_scout_group(self, user: CustomUser) -> dict | None:
        if hasattr(user, 'person') and user.person.scout_group:
            return UserScoutHierarchySerializer(user.person.scout_group, many=False, read_only=True).data
        return None

    def get_first_name(self, user: CustomUser) -> str | None:
        if hasattr(user, 'person'):
            return user.person.scout_name
        return None

    def get_scout_name(self, user: CustomUser) -> str | None:
        if hasattr(user, 'person'):
            return user.person.first_name
        return None

    def get_last_name(self, user: CustomUser) -> str | None:
        if hasattr(user, 'person'):
            return user.person.last_name
        return None


class ResponsiblePersonSerializer(serializers.ModelSerializer):
    """
    Serializer for the User model for searching users
    and selecting them as responsible person in events/registrations
    """
    email = serializers.SerializerMethodField()
    stamm = serializers.SerializerMethodField()

    class Meta:
        model = Person
        fields = (
            'scout_name',
            'email',
            'stamm',
        )

    @staticmethod
    def get_email(obj: User) -> str:
        """
        @param obj: UserExtended instance
        @return: email of connected user as str
        """
        return obj.user.email

    @staticmethod
    def get_stamm(obj: User) -> str:
        """
        @param obj: UserExtended instance
        @return: name of scout organisation of connected user as str
                 or empty string when no organisation is selected (when user is newly created=
        """
        if obj.scout_group:
            return obj.scout_group.name
        return ''


class GroupSerializer(serializers.ModelSerializer):
    """
    Serializer for the Group model
    """

    class Meta:
        model = Group
        fields = ('id', 'name',)


class EmailSettingsSerializer(serializers.ModelSerializer):
    """
    Serializer for the UserExtended model containing only email and sms notifications, so that they can be changed
    without being logged in
    """

    class Meta:
        model = User
        fields = ('email_notification', 'sms_notification')


class RegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Person
        fields = (
            'first_name',
            'last_name',
            'scout_name',
            'scout_group',
            'phone_number',
            'birthday',
            'address',
            'address_supplement',
            'zip_code',
            'gender',
            'scout_level',
            'leader',
            'bundespost',
            'email',
            'email_notification',
            'sms_notification',
            'dsgvo_confirmed',
            'username',
            'password'
        )

    username = serializers.CharField(required=True)
    password = serializers.CharField(required=True)
    dsgvo_confirmed = serializers.BooleanField(required=True)
    email_notification = serializers.CharField(max_length=10, required=False)
    sms_notification = serializers.BooleanField(required=False)
    zip_code = serializers.CharField(required=True)


class PersonSerializer(serializers.ModelSerializer):
    zip_code = ZipCodeDetailedSerializer(many=False, required=False, read_only=True)
    scout_group = ScoutHierarchyDetailedSerializer(many=False, required=False, read_only=True)
    bundespost = serializers.CharField(source='get_bundespost_display')
    gender = serializers.CharField(source='get_gender_display')
    scout_level = serializers.CharField(source='get_scout_level_display')
    leader = serializers.CharField(source='get_leader_display')
    eat_habits = EatHabitSerializer(many=True, required=False, read_only=True)

    class Meta:
        model = Person
        fields = (
            'id',
            'scout_name',
            'first_name',
            'last_name',
            'address',
            'address_supplement',
            'zip_code',
            'scout_group',
            'phone_number',
            'email',
            'bundespost',
            'birthday',
            'gender',
            'eat_habits',
            'leader',
            'scout_level',
        )


class MemberUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            'username',
            'email'
        )


class MemberSerializer(serializers.ModelSerializer):
    zip_code = ZipCodeDetailedSerializer(many=False, required=False, read_only=True)
    scout_group = ScoutHierarchyDetailedSerializer(many=False, required=False, read_only=True)
    bundespost = serializers.CharField(source='get_bundespost_display')
    gender = serializers.CharField(source='get_gender_display')
    scout_level = serializers.CharField(source='get_scout_level_display')
    leader = serializers.CharField(source='get_leader_display')
    user = MemberUserSerializer(many=False)

    class Meta:
        model = Person
        fields = (
            'id',
            'scout_name',
            'first_name',
            'last_name',
            'address',
            'address_supplement',
            'zip_code',
            'scout_group',
            'phone_number',
            'email',
            'bundespost',
            'birthday',
            'gender',
            'leader',
            'scout_level',
            'user'
        )


class EditPersonSerializer(serializers.Serializer):
    email = serializers.CharField(required=False)
    dsgvo_confirmed = serializers.BooleanField(required=False)
    email_notification = serializers.ChoiceField(required=False, choices=EmailNotificationType.choices)
    sms_notification = serializers.BooleanField(required=False)
    scout_name = serializers.CharField(required=False)
    first_name = serializers.CharField(required=False)
    last_name = serializers.CharField(required=False)
    birthday = serializers.DateField(required=False)
    address = serializers.CharField(required=False)
    address_supplement = serializers.CharField(required=False)
    zip_code = serializers.IntegerField(required=False)
    scout_group = serializers.IntegerField(required=False)
    phone_number = serializers.CharField(required=False)
    bundespost = serializers.ChoiceField(required=False, choices=BundesPostTextChoice.choices)
    gender = serializers.ChoiceField(required=False, choices=Gender.choices)
    eat_habits = serializers.ListSerializer(child=serializers.CharField(), required=False)
    leader = serializers.ChoiceField(required=False, choices=LeaderTypes.choices)
    scout_level = serializers.ChoiceField(required=False, choices=ScoutLevelTypes.choices)


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        exclude = (
            'password',
            'keycloak_id',
            'username'
        )
        extra_kwargs = {'email': {'validators': [EmailValidator, ]}}


class FullUserSerializer(serializers.ModelSerializer):
    """
    Serializer for the UserExtended model for Get/list/Retrieve requests
    """
    person = PersonSerializer(many=False)
    email_notification = serializers.CharField(source='get_email_notification_display')

    class Meta:
        model = User
        fields = (
            'dsgvo_confirmed',
            'email_notification',
            'sms_notification',
            'person',
            'username',
        )

    def to_representation(self, obj):
        """Move fields from person to user representation."""
        representation = super().to_representation(obj)
        person_representation = representation.pop('person')
        for key in person_representation:
            representation[key] = person_representation[key]

        return representation


class RequestGroupAccessSerializer(serializers.ModelSerializer):
    class Meta:
        model = RequestGroupAccess
        fields = ('user',)


class GroupRequestGroupAccessSerializer(serializers.ModelSerializer):
    parent = serializers.SerializerMethodField()
    id = serializers.SerializerMethodField()

    class Meta:
        model = KeycloakGroup
        fields = (
            'name',
            'id',
            'parent'
        )

    def get_parent(self, obj: KeycloakGroup):
        if obj.parent is not None:
            return GroupRequestGroupAccessSerializer(obj.parent).data
        else:
            return None

    def get_id(self, obj: KeycloakGroup):
        return obj.keycloak_id


class StatusRequestGroupAccessPutSerializer(serializers.ModelSerializer):
    class Meta:
        model = RequestGroupAccess
        fields = '__all__'


class StatusRequestGroupGetAccessSerializer(serializers.ModelSerializer):
    user = UserRequestSerializer(many=False, read_only=True)
    status = serializers.CharField(source='get_status_display')
    checked_by = UserRequestSerializer(many=False, read_only=True)
    group = GroupRequestGroupAccessSerializer(many=False, read_only=True)

    class Meta:
        model = RequestGroupAccess
        fields = '__all__'


class CheckUsernameSerializer(serializers.Serializer):  # noqa
    username = serializers.CharField(required=True)


class CheckEmailSerializer(serializers.Serializer):  # noqa
    email = serializers.EmailField(required=True)


class CheckPasswordSerializer(serializers.Serializer):  # noqa
    password = serializers.CharField(required=True)
