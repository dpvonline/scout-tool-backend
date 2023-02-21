from django.contrib.auth import get_user_model
from notifications.models import Notification
from rest_framework import serializers

from authentication.models import RequestGroupAccess, CustomUser
from authentication.serializers import UserRequestSerializer, GroupRequestGroupAccessSerializer
from keycloak_auth.models import KeycloakGroup
from keycloak_auth.serializers import GroupParentSerializer

User: CustomUser = get_user_model()


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
    sender = serializers.SerializerMethodField()
    target_type = serializers.SerializerMethodField()

    class Meta:
        model = Notification
        fields = (
            'id',
            'target',
            'level',
            'unread',
            'verb',
            'timestamp',
            'public',
            'emailed',
            'data',
            'sender',
            'target_type'
        )

    def get_sender(self, obj: Notification):
        if obj.actor_object_id:
            sender = User.objects.filter(id=obj.actor_object_id)
            if sender:
                return UserRequestSerializer(sender.first()).data

        return ''

    def get_target_type(self, obj: Notification):
        if obj.target_content_type:
            return obj.target_content_type.model

        return ''

class UpdateNotificationSerializer(serializers.Serializer):  # noqa
    ids = serializers.ListSerializer(child=serializers.IntegerField(), required=False)
