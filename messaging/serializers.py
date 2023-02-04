from rest_framework import serializers

from django.contrib.auth import get_user_model

from messaging.models import MessageType, Message

User = get_user_model()


class MessageTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = MessageType
        fields = '__all__'


class MessageReadSerializer(serializers.ModelSerializer):
    supervisor = serializers.SlugRelatedField(
        many=False,
        required=False,
        read_only=False,
        slug_field='email',
        queryset=User.objects.all()
    )
    message_type = MessageTypeSerializer(many=False, read_only=True)

    class Meta:
        model = Message
        fields = '__all__'

class MessageSerializer(serializers.ModelSerializer):
    supervisor = serializers.SlugRelatedField(
        many=False,
        required=False,
        read_only=False,
        slug_field='email',
        queryset=User.objects.all()
    )
    class Meta:
        model = Message
        fields = '__all__'
