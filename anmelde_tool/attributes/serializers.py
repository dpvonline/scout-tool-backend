from rest_framework import serializers

from basic.serializers import TagTypeShortSerializer
from . import models as attribute_models
from .polymorphic_serializer import PolymorphicSerializer

"""
# noqa turn off pycharm warnings about missing abstract methods, which is a bug of pycharm
"""


class AbstractAttributeSerializer(serializers.ModelSerializer):  # noqa
    type = TagTypeShortSerializer(many=False)

    class Meta:
        model = attribute_models.AbstractAttribute
        exclude = ('template', 'polymorphic_ctype')


class BooleanAttributeGetSerializer(serializers.ModelSerializer):  # noqa
    type = TagTypeShortSerializer(many=False)

    class Meta:
        model = attribute_models.BooleanAttribute
        exclude = ('template', 'polymorphic_ctype', 'in_summary')


class TimeAttributeGetSerializer(serializers.ModelSerializer):  # noqa
    type = TagTypeShortSerializer(many=False)

    class Meta:
        model = attribute_models.TimeAttribute
        exclude = ('template', 'polymorphic_ctype', 'in_summary')


class IntegerAttributeGetSerializer(serializers.ModelSerializer):  # noqa
    type = TagTypeShortSerializer(many=False)

    class Meta:
        model = attribute_models.IntegerAttribute
        exclude = ('template', 'polymorphic_ctype', 'in_summary')


class FloatAttributeGetSerializer(serializers.ModelSerializer):  # noqa
    type = TagTypeShortSerializer(many=False)

    class Meta:
        model = attribute_models.FloatAttribute
        exclude = ('template', 'polymorphic_ctype', 'in_summary')


class TravelAttributeGetSerializer(serializers.ModelSerializer):  # noqa
    type = TagTypeShortSerializer(many=False)
    type_field = serializers.CharField(source='get_type_field_display')

    class Meta:
        model = attribute_models.TravelAttribute
        exclude = ('template', 'polymorphic_ctype', 'in_summary')


class StringAttributeGetSerializer(serializers.ModelSerializer):  # noqa
    type = TagTypeShortSerializer(many=False)

    class Meta:
        model = attribute_models.StringAttribute
        exclude = ('template', 'polymorphic_ctype', 'in_summary')


class AbstractAttributeGetPolymorphicSerializer(PolymorphicSerializer):
    model_serializer_mapping = {
        attribute_models.FloatAttribute: FloatAttributeGetSerializer,
        attribute_models.IntegerAttribute: IntegerAttributeGetSerializer,
        attribute_models.TimeAttribute: TimeAttributeGetSerializer,
        attribute_models.BooleanAttribute: BooleanAttributeGetSerializer,
        attribute_models.TravelAttribute: TravelAttributeGetSerializer,
        attribute_models.StringAttribute: StringAttributeGetSerializer
    }


class BooleanAttributePutSerializer(serializers.ModelSerializer):
    class Meta:
        model = attribute_models.BooleanAttribute
        fields = ('boolean_field',)


class TimeAttributePutSerializer(serializers.ModelSerializer):
    class Meta:
        model = attribute_models.TimeAttribute
        fields = ('date_field',)


class IntegerAttributePutSerializer(serializers.ModelSerializer):
    class Meta:
        model = attribute_models.IntegerAttribute
        fields = ('integer_field',)


class FloatAttributePutSerializer(serializers.ModelSerializer):
    class Meta:
        model = attribute_models.FloatAttribute
        fields = ('float_field',)


class TravelAttributePutSerializer(serializers.ModelSerializer):
    class Meta:
        model = attribute_models.TravelAttribute
        fields = ('type_field', 'date_time_field', 'number_persons', 'description')


class StringAttributePutSerializer(serializers.ModelSerializer):
    class Meta:
        model = attribute_models.StringAttribute
        fields = ('string_field',)


class AbstractAttributePutPolymorphicSerializer(PolymorphicSerializer):
    model_serializer_mapping = {
        attribute_models.FloatAttribute: FloatAttributePutSerializer,
        attribute_models.IntegerAttribute: IntegerAttributePutSerializer,
        attribute_models.TimeAttribute: TimeAttributePutSerializer,
        attribute_models.BooleanAttribute: BooleanAttributePutSerializer,
        attribute_models.TravelAttribute: TravelAttributePutSerializer,
        attribute_models.StringAttribute: StringAttributePutSerializer
    }


class BooleanAttributeTemplatePostSerializer(serializers.ModelSerializer):
    resourcetype = serializers.CharField()

    class Meta:
        model = attribute_models.BooleanAttribute
        fields = ('boolean_field', 'resourcetype', 'template_id')


class TimeAttributeTemplatePostSerializer(serializers.ModelSerializer):
    resourcetype = serializers.CharField()

    class Meta:
        model = attribute_models.TimeAttribute
        fields = ('date_field', 'resourcetype', 'template_id')


class IntegerAttributeTemplatePostSerializer(serializers.ModelSerializer):
    resourcetype = serializers.CharField()

    class Meta:
        model = attribute_models.IntegerAttribute
        fields = ('integer_field', 'resourcetype', 'template_id')


class FloatAttributeTemplatePostSerializer(serializers.ModelSerializer):
    resourcetype = serializers.CharField()

    class Meta:
        model = attribute_models.FloatAttribute
        fields = ('float_field', 'resourcetype', 'template_id')


class TravelAttributeTemplatePostSerializer(serializers.ModelSerializer):
    resourcetype = serializers.CharField()

    class Meta:
        model = attribute_models.TravelAttribute
        fields = ('type_field', 'date_time_field', 'persons', 'description', 'resourcetype', 'template_id')


class StringAttributeTemplatePostSerializer(serializers.ModelSerializer):
    resourcetype = serializers.CharField()

    class Meta:
        model = attribute_models.StringAttribute
        fields = ('string_field', 'resourcetype', 'template_id')


class AbstractAttributeTemplatePostPolymorphicSerializer(PolymorphicSerializer):
    model_serializer_mapping = {
        attribute_models.FloatAttribute: FloatAttributeTemplatePostSerializer,
        attribute_models.IntegerAttribute: IntegerAttributeTemplatePostSerializer,
        attribute_models.TimeAttribute: TimeAttributeTemplatePostSerializer,
        attribute_models.BooleanAttribute: BooleanAttributeTemplatePostSerializer,
        attribute_models.TravelAttribute: TravelAttributeTemplatePostSerializer,
        attribute_models.StringAttribute: StringAttributeTemplatePostSerializer
    }


class BooleanAttributePostSerializer(serializers.ModelSerializer):
    class Meta:
        model = attribute_models.BooleanAttribute
        fields = '__all__'


class TimeAttributePostSerializer(serializers.ModelSerializer):
    class Meta:
        model = attribute_models.TimeAttribute
        fields = '__all__'


class IntegerAttributePostSerializer(serializers.ModelSerializer):
    class Meta:
        model = attribute_models.IntegerAttribute
        fields = '__all__'


class FloatAttributePostSerializer(serializers.ModelSerializer):
    class Meta:
        model = attribute_models.FloatAttribute
        fields = '__all__'


class TravelAttributePostSerializer(serializers.ModelSerializer):
    class Meta:
        model = attribute_models.TravelAttribute
        fields = '__all__'


class StringAttributePostSerializer(serializers.ModelSerializer):
    class Meta:
        model = attribute_models.StringAttribute
        fields = '__all__'


class AbstractAttributePostPolymorphicSerializer(PolymorphicSerializer):
    model_serializer_mapping = {
        attribute_models.FloatAttribute: FloatAttributePostSerializer,
        attribute_models.IntegerAttribute: IntegerAttributePostSerializer,
        attribute_models.TimeAttribute: TimeAttributePostSerializer,
        attribute_models.BooleanAttribute: BooleanAttributePostSerializer,
        attribute_models.TravelAttribute: TravelAttributePostSerializer,
        attribute_models.StringAttribute: StringAttributePostSerializer
    }
