from rest_framework import serializers

from anmelde_tool.attributes import models as attribute_models

"""
# noqa turn off pycharm warnings about missing abstract methods, which is a bug of pycharm
"""


class AttributeModuleSerializer(serializers.ModelSerializer):
    class Meta:
        model = attribute_models.AttributeModule
        fields = '__all__'


class AttributeModuleEventReadSerializer(serializers.ModelSerializer):
    field_type = serializers.CharField(source='get_field_type_display', read_only=True)

    class Meta:
        model = attribute_models.AttributeModule
        exclude = (
            'event_module',
            'standard'
        )


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
