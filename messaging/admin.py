from django.contrib import admin

from messaging.models import Message, MessageType

admin.site.register(Message)
admin.site.register(MessageType)
