from rest_framework import serializers

from django.contrib.auth import get_user_model

from messaging.models import MessageType, Message

from authentication.serializers import UserRequestSerializer

User = get_user_model()


class MessageTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = MessageType
        fields = '__all__'

class MessageInternSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = '__all__'


class MessageReadSerializer(serializers.ModelSerializer):
    created_by = UserRequestSerializer(many=False, read_only=True)
    supervisor = UserRequestSerializer(many=False, read_only=True)
    message_type = MessageTypeSerializer(many=False, read_only=True)

    class Meta:
        model = Message
        fields = '__all__'

class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = '__all__'
