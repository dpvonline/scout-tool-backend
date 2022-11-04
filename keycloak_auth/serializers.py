from abc import ABC

from django.contrib.auth import get_user_model
from rest_framework import serializers

from authentication.models import CustomUser, Person
from authentication.serializers import UserScoutHierarchySerializer

User: CustomUser = get_user_model()


class PersonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Person
        exclude = (
            'active',
            'person_verified',
        )


class UserListSerializer(serializers.ModelSerializer):
    """
    Serializer for the UserExtended model for Get/list/Retrieve requests
    """
    scout_organisation = UserScoutHierarchySerializer(many=False)

    class Meta:
        model = User
        exclude = (
            'keycloak_id',
            'password'
        )


class CreateGroupSerializer(serializers.Serializer):
    name = serializers.CharField(required=True)
    parent_id = serializers.CharField(required=False)


class UpdateGroupSerializer(serializers.Serializer):
    name = serializers.CharField(required=False)
    parent_id = serializers.CharField(required=False)
