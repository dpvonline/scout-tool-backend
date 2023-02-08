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
from keycloak_auth.models import KeycloakGroup, ExternalLinks
from keycloak_auth.permissions import request_group_access

User: CustomUser = get_user_model()


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
    parent_id = serializers.CharField(required=False)
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
            'is_member'
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
        admin_perm = request_group_access(request, obj.keycloak_id, PermissionType.ADMIN)
        if admin_perm:
            return "Administrator"
        view_perm = request_group_access(request, obj.keycloak_id, PermissionType.VIEW)
        if view_perm:
            return "Ansicht"
        return PermissionType.NONE

    def get_is_member(self, obj: KeycloakGroup) -> bool:
        request = self.context.get('request')
        token = request.META.get('HTTP_AUTHORIZATION')
        try:
            keycloak_groups = keycloak_user.get_user_groups(
                token,
                request.user.keycloak_id,
                brief_representation=True
            )
        except KeycloakGetError:
            raise NotAuthorized()

        if any(obj.keycloak_id == group['id'] for group in keycloak_groups):
            return True

        return False


class PartialUserSerializer(serializers.ModelSerializer):
    """
    Serializer for the UserExtended model for Get/list/Retrieve requests
    """
    person = PersonSerializer(many=False)
    id = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'id',
            'person',
            'keycloak_id',
        )

    def get_id(self, obj: KeycloakGroup):
        return obj.keycloak_id
