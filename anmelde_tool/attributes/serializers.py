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
    type = serializers.ReadOnlyField(default='booleanAttribute')
    attribute_module = AttributeModuleEventReadSerializer(read_only=True)

    class Meta:
        model = attribute_models.BooleanAttribute
        fields = '__all__'


class TimeAttributeSerializer(serializers.ModelSerializer):
    type = serializers.ReadOnlyField(default='timeAttribute')
    attribute_module = AttributeModuleEventReadSerializer(read_only=True)

    class Meta:
        model = attribute_models.TimeAttribute
        fields = '__all__'


class IntegerAttributeSerializer(serializers.ModelSerializer):
    type = serializers.ReadOnlyField(default='integerAttribute')
    attribute_module = AttributeModuleEventReadSerializer(read_only=True)

    class Meta:
        model = attribute_models.IntegerAttribute
        fields = '__all__'


class FloatAttributeSerializer(serializers.ModelSerializer):
    type = serializers.ReadOnlyField(default='floatAttribute')
    attribute_module = AttributeModuleEventReadSerializer(read_only=True)

    class Meta:
        model = attribute_models.FloatAttribute
        fields = '__all__'


class StringAttributeSerializer(serializers.ModelSerializer):
    type = serializers.ReadOnlyField(default='stringAttribute')
    attribute_module = AttributeModuleEventReadSerializer(read_only=True)

    class Meta:
        model = attribute_models.StringAttribute
        fields = '__all__'


class TravelAttributeSerializer(serializers.ModelSerializer):
    type = serializers.ReadOnlyField(default='travelAttribute')
    attribute_module = AttributeModuleEventReadSerializer(read_only=True)

    class Meta:
        model = attribute_models.TravelAttribute
        fields = '__all__'


class BooleanAttributePostSerializer(serializers.Serializer):
    attribute_module = serializers.IntegerField(required=True)
    boolean_field = serializers.BooleanField(required=True)


class TimeAttributePostSerializer(serializers.Serializer):
    attribute_module = serializers.IntegerField(required=True)
    time_field = serializers.CharField(required=True)


class IntegerAttributePostSerializer(serializers.Serializer):
    attribute_module = serializers.IntegerField(required=True)
    integer_field = serializers.IntegerField(required=True)


class FloatAttributePostSerializer(serializers.Serializer):
    attribute_module = serializers.IntegerField(required=True)
    float_field = serializers.FloatField(required=True)


class StringAttributePostSerializer(serializers.Serializer):
    attribute_module = serializers.IntegerField(required=True)
    string_field = serializers.CharField(required=True)


class TravelAttributePostSerializer(serializers.ModelSerializer):
    attribute_module = serializers.IntegerField(required=True)

    class Meta:
        model = attribute_models.TravelAttribute
        fields = (
            'number_persons',
            'type_field',
            'date_time_field',
            'description',
            'attribute_module'
        )


class BooleanUpdateAttributeSerializer(serializers.ModelSerializer):
    class Meta:
        model = attribute_models.BooleanAttribute
        exclude = (
            'registration',
            'attribute_module'
        )


class TimeUpdateAttributeSerializer(serializers.ModelSerializer):
    class Meta:
        model = attribute_models.TimeAttribute
        exclude = (
            'registration',
            'attribute_module'
        )


class IntegerUpdateAttributeSerializer(serializers.ModelSerializer):
    class Meta:
        model = attribute_models.IntegerAttribute
        exclude = (
            'registration',
            'attribute_module'
        )


class FloatUpdateAttributeSerializer(serializers.ModelSerializer):
    class Meta:
        model = attribute_models.FloatAttribute
        exclude = (
            'registration',
            'attribute_module'
        )


class StringUpdateAttributeSerializer(serializers.ModelSerializer):
    class Meta:
        model = attribute_models.StringAttribute
        exclude = (
            'registration',
            'attribute_module'
        )


class TravelUpdateAttributeSerializer(serializers.ModelSerializer):
    class Meta:
        model = attribute_models.TravelAttribute
        exclude = (
            'registration',
            'attribute_module'
        )
