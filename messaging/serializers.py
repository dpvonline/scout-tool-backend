from email import message
from rest_framework import serializers

from django.contrib.auth import get_user_model

from messaging.models import IssueType, Message, Issue

from authentication.serializers import UserRequestSerializer
from keycloak_auth.serializers import FullGroupSerializer

User = get_user_model()


class IssueTypeReadSerializer(serializers.ModelSerializer):
    responsable_groups = FullGroupSerializer(many=True, read_only=True)

    class Meta:
        model = IssueType
        fields = '__all__'

class IssueTypeReadShortSerializer(serializers.ModelSerializer):

    class Meta:
        model = IssueType
        fields = (
            'id',
            'name',
            'description',
            'sorting'
        )


class IssueTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = IssueType
        fields = '__all__'


class IssueReadSerializer(serializers.ModelSerializer):
    messages = serializers.SerializerMethodField()
    created_by = UserRequestSerializer(many=False, read_only=True)
    issue_type = IssueTypeReadSerializer(many=False, read_only=True)
    processors = UserRequestSerializer(many=True, read_only=True)
    
    def get_messages(self, obj):
        messages = Message.objects.filter(issue=obj.id).order_by('-created_at', '-updated_at')
        return MessageReadSerializer(messages, many=True).data

    class Meta:
        model = Issue
        fields = '__all__'


class IssueSerializer(serializers.ModelSerializer):
    class Meta:
        model = Issue
        fields = '__all__'


class MessageReadSerializer(serializers.ModelSerializer):
    issue = IssueSerializer(many=False, read_only=False)
    created_by = UserRequestSerializer(many=False, read_only=True)
    
    class Meta:
        model = Message
        fields = '__all__'

class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = '__all__'
