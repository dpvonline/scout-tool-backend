from django.db import models

from anmelde_tool.attributes.choices import TravelType
from basic.models import TagType
from anmelde_tool.event.models import Registration


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
