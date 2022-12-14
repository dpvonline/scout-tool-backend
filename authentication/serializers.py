from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from rest_framework import serializers

from anmelde_tool.event.choices.choices import Gender, ScoutLevelTypes, LeaderTypes
from authentication.choices import BundesPostTextChoice
from authentication.models import CustomUser
from basic.models import ScoutHierarchy

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
        seaches in the ScoutHierachy for the parent having the level `Bund` and returns the filtered name
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

    class Meta:
        model = User
        fields = (
            'mobile_number',
            'scout_name',
        )


class ResponsiblePersonSerializer(serializers.ModelSerializer):
    """
    Serializer for the User model for searching users
    and selecting them as responsible person in events/registrations
    """
    email = serializers.SerializerMethodField()
    stamm = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'scout_name',
            'email',
            'stamm',
            'user'
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
        if obj.scout_organisation:
            return obj.scout_organisation.name
        return ''


class UserGetSerializer(serializers.ModelSerializer):
    """
    Serializer for the UserExtended model for Get/list/Retrieve requests
    """
    scout_organisation = UserScoutHierarchySerializer()

    class Meta:
        model = User
        fields = (
            'id',
            'mobile_number',
            'scout_name',
            'scout_organisation',
            'dsgvo_confirmed'
        )


class UserPostSerializer(serializers.ModelSerializer):
    """
    Serializer for the UserExtended model for create/update/patch requests
    containing less information that the get pendent
    """

    class Meta:
        model = User
        fields = (
            'mobile_number',
            'scout_name',
            'scout_organisation',
            'dsgvo_confirmed'
        )


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
        model = User
        fields = (
            'first_name',
            'last_name',
            'scout_name',
            'email',
            'scout_organisation',
            'mobile_number',
            'email_notification',
            'sms_notification',
            'dsgvo_confirmed',
            'username',
            'password',
            'birth_date',
            'address',
            'additional_address',
            'zip_code',
            'gender',
            'scout_level',
            'leader',
            'bundespost'
        )

    birth_date = serializers.DateField(required=False)
    address = serializers.CharField(required=False)
    additional_address = serializers.CharField(required=False)
    zip_code = serializers.IntegerField(required=False)
    gender = serializers.ChoiceField(required=False, choices=Gender.choices)
    scout_level = serializers.ChoiceField(required=False, choices=ScoutLevelTypes.choices)
    leader = serializers.ChoiceField(required=False, choices=LeaderTypes.choices)
    bundespost = serializers.ChoiceField(required=False, choices=BundesPostTextChoice.choices)
