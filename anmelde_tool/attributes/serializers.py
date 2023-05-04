from rest_framework import serializers

from basic.serializers import TagTypeShortSerializer
from anmelde_tool.attributes import models as attribute_models

"""
# noqa turn off pycharm warnings about missing abstract methods, which is a bug of pycharm
"""


class AttributeEventModuleMapperSerializer(serializers.ModelSerializer):
    class Meta:
        model = attribute_models.AttributeEventModuleMapper
        fields = '__all__'


class BooleanAttributeSerializer(serializers.ModelSerializer):
    class Meta:
        model = attribute_models.BooleanAttribute
        fields = '__all__'


class TimeAttributeSerializer(serializers.ModelSerializer):
    class Meta:
        model = attribute_models.TimeAttribute
        fields = '__all__'


class IntegerAttributeSerializer(serializers.ModelSerializer):
    class Meta:
        model = attribute_models.IntegerAttribute
        fields = '__all__'


class FloatAttributeSerializer(serializers.ModelSerializer):
    class Meta:
        model = attribute_models.FloatAttribute
        fields = '__all__'


class StringAttributeSerializer(serializers.ModelSerializer):
    class Meta:
        model = attribute_models.StringAttribute
        fields = '__all__'


class TravelAttributeSerializer(serializers.ModelSerializer):
    class Meta:
        model = attribute_models.TravelAttribute
        fields = '__all__'
