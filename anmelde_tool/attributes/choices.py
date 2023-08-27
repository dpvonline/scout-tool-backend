from django.db import models
from django.utils.translation import gettext_lazy as _


class TravelType(models.TextChoices):
    Train = 'T', _('Öffis')
    Bus = 'B', _('Reisebus')
    Car = 'C', _('PKW')
    Other = 'O', _('Sonstiges')


class AttributeType(models.TextChoices):
    BooleanAttribute = 'BoA', _('booleanAttribute')
    DateTimeAttribute = 'TiA', _('dateTimeAttribute')
    IntegerAttribute = 'InA', _('integerAttribute')
    FloatAttribute = 'FlA', _('floatAttribute')
    StringAttribute = 'StA', _('stringAttribute')
    TravelAttribute = 'TrA', _('travelAttribute')
