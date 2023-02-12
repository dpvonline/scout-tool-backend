import uuid
from django.contrib.auth import get_user_model
from django.db import models

from basic.models import TimeStampMixin
from keycloak_auth.models import KeycloakGroup
from messaging.choices import MessageStatusChoise, MessagePriorityChoise

User = get_user_model()


class IssueType(TimeStampMixin):
    id = models.AutoField(auto_created=True, primary_key=True)
    name = models.CharField(max_length=30)
    is_public = models.BooleanField(default=False)
    description = models.CharField(max_length=100, blank=True)
    responsable_groups = models.ManyToManyField(KeycloakGroup, blank=True)
    sorting = models.IntegerField(
        blank=False, auto_created=True, unique=True, null=True)

    def __str__(self):
        return self.name

    def __repr__(self):
        return self.__str__()


class Issue(TimeStampMixin):
    id = models.UUIDField(auto_created=True, primary_key=True, default=uuid.uuid4, editable=False)
    issue_type = models.ForeignKey(IssueType, on_delete=models.PROTECT)
    created_by_name = models.CharField(max_length=60, blank=True, null=True)
    created_by_email = models.CharField(max_length=60, blank=True, null=True)
    created_by = models.ForeignKey(User, on_delete=models.PROTECT, null=True, blank=True, related_name="issue_created_by")
    processors = models.ManyToManyField(User, blank=True)
    priority = models.CharField(
        max_length=30,
        choices=MessagePriorityChoise.choices,
        default=MessagePriorityChoise.NORMAL,
    )
    status = models.CharField(
        max_length=30,
        choices=MessageStatusChoise.choices,
        default=MessageStatusChoise.UNREAD,
    )
    issue_subject = models.CharField(max_length=100, blank=True, null=True)


    def __str__(self):
        return self.issue_subject

    def __repr__(self):
        return self.__str__()


class Message(TimeStampMixin):
    id = models.AutoField(auto_created=True, primary_key=True)
    created_by = models.ForeignKey(User, on_delete=models.PROTECT, null=True, blank=True, related_name="message_created_by")
    issue = models.ForeignKey(Issue, on_delete=models.PROTECT, related_name="issue", blank=True, null=True)
    message_body = models.CharField(max_length=10000)
    is_public = models.BooleanField(default=False)
    has_been_read = models.BooleanField(default=False)


    def __str__(self):
        return self.message_body

    def __repr__(self):
        return self.__str__()
