from django.db import models
from django.utils.translation import gettext_lazy as _


class TravelType(models.TextChoices):
    Train = 'T', _('Bahn')
    Bus = 'B', _('Reisebus')
    Car = 'C', _('PKW')
    Other = 'O', _('Sonstiges')


class AttributeType(models.TextChoices):
    BooleanAttribute = 'BoA', _('booleanAttribute')
    TimeAttribute = 'TiA', _('timeAttribute')
    IntegerAttribute = 'InA', _('integerAttribute')
    FloatAttribute = 'FlA', _('floatAttribute')
    StringAttribute = 'StA', _('stringAttribute')
    TravelAttribute = 'TrA', _('travelAttribute')
