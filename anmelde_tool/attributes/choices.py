from django.db import models
from django.utils.translation import gettext_lazy as _


class TravelType(models.TextChoices):
    Train = 'T', _('Bahn')
    Bus = 'B', _('Reisebus')
    Car = 'C', _('PKW')
    Other = 'O', _('Sonstiges')

class AttributeType(models.TextChoices):
    BooleanAttribute = 'BoA', _('BooleanAttribute')
    TimeAttribute = 'TiA', _('TimeAttribute')
    IntegerAttribute = 'InA', _('IntegerAttribute')
    FloatAttribute = 'FlA', _('FloatAttribute')
    StringAttribute = 'StA', _('StringAttribute')
    TravelAttribute = 'TrA', _('TravelAttribute')
