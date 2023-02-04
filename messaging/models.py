from django.contrib.auth import get_user_model
from django.db import models

from basic.models import TimeStampMixin

User = get_user_model()


class MessageType(TimeStampMixin):
    id = models.AutoField(auto_created=True, primary_key=True)
    name = models.CharField(max_length=30)
    is_comment = models.BooleanField(default=False)
    description = models.CharField(max_length=100, blank=True)
    sorting = models.IntegerField(
        blank=False, auto_created=True, unique=True, null=True)

    def __str__(self):
        return self.name

    def __repr__(self):
        return self.__str__()


class Message(TimeStampMixin):
    id = models.AutoField(auto_created=True, primary_key=True)
    created_by_email = models.CharField(max_length=60, blank=True, null=True)
    supervisor = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    message_type = models.ForeignKey(MessageType, on_delete=models.CASCADE)
    message_subject = models.CharField(max_length=100, blank=True, null=True)
    message_body = models.CharField(max_length=10000)
    internal_comment = models.CharField(max_length=10000, blank=True, null=True)
    is_processed = models.BooleanField(default=False)

    def __str__(self):
        return self.message_subject

    def __repr__(self):
        return self.__str__()
