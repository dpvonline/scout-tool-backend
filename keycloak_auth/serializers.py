from django.contrib.auth import get_user_model
from keycloak import KeycloakGetError
from rest_framework import serializers

from authentication.models import CustomUser, Person
from authentication.serializers import UserScoutHierarchySerializer
from backend.settings import keycloak_user, keycloak_admin
from basic.serializers import ScoutHierarchySerializer
from keycloak_auth.api_exceptions import NotAuthorized
from keycloak_auth.choices import CreateGroupChoices
from keycloak_auth.enums import PermissionType
from keycloak_auth.helper import get_groups_of_user
from keycloak_auth.models import KeycloakGroup, ExternalLinks
from keycloak_auth.permissions import request_group_access

User: CustomUser = get_user_model()

def get_display_name_user(obj: User):
    if hasattr(obj, 'person') and obj.person.scout_name:
        return obj.person.scout_name
    else:
        return obj.username


def get_display_name_group(obj: KeycloakGroup):
    if hasattr(obj, 'scouthierarchy') and obj.scouthierarchy:
        return obj.scouthierarchy.name

    if obj.parent:
        if hasattr(obj.parent, 'scouthierarchy') and obj.parent.scouthierarchy:
            return f'{obj.name} <- {obj.parent.scouthierarchy}'
        else:
            return f'{obj.name} <- {obj.parent.name}'

    return obj.name


class PersonSerializer(serializers.ModelSerializer):
    scout_group = UserScoutHierarchySerializer(many=False)

    class Meta:
        model = Person
        fields = (
            'id',
            'scout_name',
            'first_name',
            'scout_group'
        )


class UserListSerializer(serializers.ModelSerializer):
    """
    Serializer for the UserExtended model for Get/list/Retrieve requests
    """
    person = PersonSerializer(many=False, read_only=True)
    id = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'id',
            'keycloak_id',
            'person'
        )

    def get_id(self, obj: KeycloakGroup):
        return obj.keycloak_id


class CreateGroupSerializer(serializers.Serializer):
    name = serializers.CharField(required=True)
    parent_id = serializers.CharField(required=True)
    type = serializers.ChoiceField(required=True, choices=CreateGroupChoices.choices)


class UpdateGroupSerializer(serializers.Serializer):
    name = serializers.CharField(required=False)
    parent_id = serializers.CharField(required=False)


class GroupParentSerializer(serializers.ModelSerializer):
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
            return GroupParentSerializer(obj.parent).data
        else:
            return None

    def get_id(self, obj: KeycloakGroup):
        return obj.keycloak_id


class GroupChildrenSerializer(serializers.ModelSerializer):
    id = serializers.SerializerMethodField()

    class Meta:
        model = KeycloakGroup
        fields = (
            'name',
            'id'
        )

    def get_id(self, obj: KeycloakGroup):
        return obj.keycloak_id


class ExternalLinksSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExternalLinks
        fields = (
            'wiki',
            'cloud'
        )


class FullGroupSerializer(serializers.ModelSerializer):
    parent = serializers.SerializerMethodField()
    id = serializers.SerializerMethodField()
    children = serializers.SerializerMethodField()
    permission = serializers.SerializerMethodField()
    is_member = serializers.SerializerMethodField()
    display_name = serializers.SerializerMethodField()
    scouthierarchy = ScoutHierarchySerializer(many=False)
    externallinks = ExternalLinksSerializer(many=False)

    class Meta:
        model = KeycloakGroup
        fields = (
            'name',
            'id',
            'parent',
            'children',
            'permission',
            'membership_allowed',
            'description',
            'scouthierarchy',
            'externallinks',
            'is_member',
            'display_name'
        )

    def get_parent(self, obj: KeycloakGroup):
        if obj.parent is not None:
            return GroupParentSerializer(obj.parent).data
        else:
            return None

    def get_id(self, obj: KeycloakGroup):
        return obj.keycloak_id

    def get_children(self, obj: KeycloakGroup):
        if obj.children:
            serializer = GroupChildrenSerializer(obj.children, many=True)
            return serializer.data
        else:
            return None

    def get_permission(self, obj: KeycloakGroup) -> str:
        request = self.context.get('request')
        if request:
            admin_perm = request_group_access(request, obj.keycloak_id, PermissionType.ADMIN)
            if admin_perm:
                return "Administrator"
            view_perm = request_group_access(request, obj.keycloak_id, PermissionType.VIEW)
            if view_perm:
                return "Ansicht"
            return PermissionType.NONE
        return PermissionType.NONE

    def get_is_member(self, obj: KeycloakGroup) -> bool:
        request = self.context.get('request')
        if request and request.META:
            token = request.META.get('HTTP_AUTHORIZATION')
            ids = get_groups_of_user(token, request.user.keycloak_id)

            if any(obj.keycloak_id == group_id for group_id in ids):
                return True

        return False

    def get_display_name(self, obj: KeycloakGroup):
        return get_display_name_group(obj)


class PartialUserSerializer(serializers.ModelSerializer):
    """
    Serializer for the UserExtended model for Get/list/Retrieve requests
    """
    id = serializers.SerializerMethodField()
    django_id = serializers.SerializerMethodField()
    display_name = serializers.SerializerMethodField()
    scout_name = serializers.SerializerMethodField()
    stamm_bund = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'id',
            'django_id',
            'username',
            'keycloak_id',
            'scout_name',
            'stamm_bund',
            'display_name',
        )

    def get_id(self, obj: User):
        return obj.keycloak_id

    def get_django_id(self, obj: User):
        return obj.id

    def get_display_name(self, obj: User):
        return get_display_name_user(obj)

    def get_scout_name(self, obj: User):
        if hasattr(obj, 'person'):
            return obj.person.scout_name
        return ''

    def get_stamm_bund(self, obj: User):
        if hasattr(obj, 'person'):
            return  UserScoutHierarchySerializer(obj.person.scout_group).data
        return ''


class SearchResultUserSerializer(serializers.ModelSerializer):
    display_name = serializers.SerializerMethodField()
    id = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'id',
            'display_name'
        )

    def get_id(self, obj: User):
        if obj.keycloak_id:
            return obj.keycloak_id
        return ''

    def get_display_name(self, obj: User):
        return get_display_name_user(obj)


class MemberUserIdSerializer(serializers.Serializer):
    user_id = serializers.CharField(required=True)


class GroupShortSerializer(serializers.ModelSerializer):
    display_name = serializers.SerializerMethodField()

    class Meta:
        model = KeycloakGroup
        fields = (
            'name',
            'id',
            'keycloak_id',
            'display_name'
        )

    def get_display_name(self, obj: KeycloakGroup):
        return get_display_name_group(obj)
