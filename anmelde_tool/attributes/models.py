from django.db import models

import anmelde_tool.event.models
from anmelde_tool.attributes.choices import TravelType
from anmelde_tool.registration.models import Registration
from basic.models import TagType


class AbstractAttribute(models.Model):
    id = models.AutoField(auto_created=True, primary_key=True)
    name = models.CharField(max_length=100, blank=True)
    in_summary = models.BooleanField(default=True)
    registration = models.ForeignKey(Registration, on_delete=models.CASCADE, null=True, blank=True)

    class Meta:
        abstract = True

    def __str__(self):
        return f'{self.name}'


class BooleanAttribute(AbstractAttribute):
    boolean_field = models.BooleanField(default=False)


class TimeAttribute(AbstractAttribute):
    date_field = models.DateTimeField()


class IntegerAttribute(AbstractAttribute):
    integer_field = models.IntegerField(default=0)


class FloatAttribute(AbstractAttribute):
    float_field = models.FloatField()


class StringAttribute(AbstractAttribute):
    string_field = models.TextField(max_length=10000, blank=True, null=True)


class TravelAttribute(AbstractAttribute):
    number_persons = models.IntegerField(default=0)
    type_field = models.CharField(max_length=1, choices=TravelType.choices, null=True, blank=True)
    date_time_field = models.DateTimeField(blank=True, null=True)
    description = models.CharField(max_length=100, blank=True)


class AttributeEventModuleMapper(models.Model):
    """
    if the is_required is set to True the user has explicit do a choice or has to confirm smth.
    min_length, max_length are only relevant for attributes with texts
    tooltip = extra description which appears when hovering above the element
    """
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=1000, null=True)
    text = models.CharField(max_length=10000, null=True)
    is_required = models.BooleanField(default=False)
    min_length = models.IntegerField(default=0)
    max_length = models.IntegerField(default=0)
    tooltip = models.CharField(max_length=1000, null=True, blank=True)
    default_value = models.CharField(max_length=1000, null=True, blank=True)
    field_type = models.CharField(max_length=25, null=True, blank=True)
    icon = models.CharField(max_length=25, null=True, blank=True)
    max_entries = models.IntegerField(default=1)
    event_module = models.ForeignKey(
        anmelde_tool.event.models.EventModule,
        on_delete=models.CASCADE,
        null=True,
        blank=True
        )

    def __str__(self):
        return f'{self.title}'
