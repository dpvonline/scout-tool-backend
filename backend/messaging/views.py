from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets
from rest_framework.filters import SearchFilter

from messaging.models import Message, MessageType
from messaging.serializers import MessageSerializer, MessageTypeSerializer


class MessageViewSet(viewsets.ModelViewSet):
    queryset = Message.objects.all().order_by('created_at')
    serializer_class = MessageSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_fields = ['message_type', 'is_processed']
    search_fields = ['created_by_email', 'message_body', 'internal_comment']


class MessageTypeViewSet(viewsets.ModelViewSet):
    queryset = MessageType.objects.all()
    serializer_class = MessageTypeSerializer
