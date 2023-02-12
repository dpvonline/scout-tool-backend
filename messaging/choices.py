from django.db import models
from django.utils.translation import gettext_lazy as _


class MessageStatusChoise(models.TextChoices):
    """
    Choices for a Message Status
    """
    UNREAD = 'unread', _('Ungelesen')
    WIP = 'wip', _('In Arbeit')
    SUCCESS = 'success', _('Erfolgreich')
    FAILED = 'failed', _('Nicht erfolgreich')


class MessagePriorityChoise(models.TextChoices):
    """
    Choices for a Message Status
    """
    URGENT = 'urgent', _('Eilig')
    NORMAL = 'normal', _('normal')
