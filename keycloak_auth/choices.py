from django.db import models
from django.utils.translation import gettext_lazy as _


class CreateGroupChoices(models.TextChoices):
    """
    Choices a user can select, how often he wants to receive emails"
    """
    EVENT = 'Event', _('Aktion')
    GRUPPE = 'Gruppe', _('Gruppe')
    AK = 'AK', _('Arbeitskreis')
    OTHER = 'Other', _('Sonstiges')
