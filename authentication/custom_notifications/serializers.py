from notifications.models import Notification
from rest_framework import serializers

from authentication.models import RequestGroupAccess
from authentication.serializers import UserRequestSerializer, GroupRequestGroupAccessSerializer
from keycloak_auth.models import KeycloakGroup
from keycloak_auth.serializers import GroupParentSerializer


class GenericNotificationRelatedField(serializers.RelatedField):  # noqa

    def to_representation(self, value):
        if isinstance(value, RequestGroupAccess):
            return GroupRequestGroupAccessSerializer(value).data
        if isinstance(value, KeycloakGroup):
            return GroupParentSerializer(value).data
        else:
            return None


class NotificationSerializer(serializers.ModelSerializer):
    target = GenericNotificationRelatedField(read_only=True, many=False)
    user = UserRequestSerializer(read_only=True, many=False)

    class Meta:
        model = Notification
        fields = '__all__'


class UpdateNotificationSerializer(serializers.Serializer):  # noqa
    ids = serializers.ListSerializer(child=serializers.IntegerField(), required=False)
