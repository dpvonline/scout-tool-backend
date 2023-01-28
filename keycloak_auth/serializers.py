from django.contrib.auth import get_user_model
from rest_framework import serializers

from authentication.models import CustomUser, Person
from authentication.serializers import UserScoutHierarchySerializer
from basic.serializers import ScoutHierarchySerializer
from keycloak_auth.choices import CreateGroupChoices
from keycloak_auth.enums import PermissionType
from keycloak_auth.models import KeycloakGroup
from keycloak_auth.permissions import request_group_access

User: CustomUser = get_user_model()


class PersonSerializer(serializers.ModelSerializer):
    scout_group = UserScoutHierarchySerializer(many=False)

    class Meta:
        model = Person
        fields = (
            'scout_name',
            'last_name',
            'first_name',
            'scout_group'
        )


class UserListSerializer(serializers.ModelSerializer):
    """
    Serializer for the UserExtended model for Get/list/Retrieve requests
    """
    person = PersonSerializer(many=False, read_only=True)

    class Meta:
        model = User
        fields = (
            'keycloak_id',
            'person'
        )


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
        model = KeycloakGroup
        fields = (
            'wiki',
            'cloud'
        )


class GroupSerializer(serializers.ModelSerializer):
    parent = serializers.SerializerMethodField()
    id = serializers.SerializerMethodField()
    children = serializers.SerializerMethodField()
    permission = serializers.SerializerMethodField()
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
            'scouthierarchy',
            'externallinks'
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

    def get_permission(self, obj: KeycloakGroup) -> PermissionType:
        request = self.context.get('request')
        admin_perm = request_group_access(request, obj.keycloak_id, PermissionType.ADMIN)
        if admin_perm:
            return PermissionType.ADMIN
        view_perm = request_group_access(request, obj.keycloak_id, PermissionType.VIEW)
        if view_perm:
            return PermissionType.VIEW
        return PermissionType.NONE
