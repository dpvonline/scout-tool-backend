from django.db import models
from django.utils.translation import gettext_lazy as _


class EmailNotificationType(models.TextChoices):
    """
    Choices a user can select, how often he wants to receive emails"
    """
    FULL = 'Full', _('Alles')
    EVERY_3H = '3H', _('Alle 3 Stunden')
    EVERY_12H = '12H', _('Alle 12 Stunden')
    DAILY = 'Daily', _('Täglich')
    WEEKLY = 'Weekly', _('Wöchentlich')
    IMPORTANT = 'Important', _('Nur wichtiges')


class BundesPostTextChoice(models.TextChoices):
    """
    Choices a user can select, how often he wants to receive emails"
    """
    NOTHING = 'nothing', _('Keine Bundespost')
    DIGITAL = 'digital', _('Nur Digital')
    DIGITAL_POST = 'digital_post', _('Digital und Post')
    POST = 'post', _('Nur per Post')


class RequestGroupAccessChoices(models.TextChoices):
    NONE = 'nothing', _('offen')
    ACCEPTED = 'accepted', _('akzeptiert')
    DECLINED = 'declined', _('abgelehnt')
