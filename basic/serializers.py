from rest_framework import serializers
from basic import models as basic_models

"""
# noqa turn off pycharm warnings about missing abstract methods, which is a bug of pycharm
"""


def get_parent_scout_organisation(obj: basic_models.ScoutHierarchy, filter_level: str) -> str:
    iterator: basic_models.ScoutHierarchy = obj
    while iterator is not None:
        if iterator.level.name == filter_level:
            return iterator.name
        iterator = iterator.parent

    return ''


class ScoutHierarchySerializer(serializers.ModelSerializer):
    class Meta:
        model = basic_models.ScoutHierarchy
        fields = '__all__'


class NameOnlyScoutHierarchySerializer(serializers.ModelSerializer):
    class Meta:
        model = basic_models.ScoutHierarchy
        fields = ('name',)


class ZipCodeShortSerializer(serializers.ModelSerializer):
    class Meta:
        model = basic_models.ZipCode
        fields = ('zip_code', 'city')


class ZipCodeSerializer(serializers.ModelSerializer):
    class Meta:
        model = basic_models.ZipCode
        fields = '__all__'


class ScoutOrgaLevelSerializer(serializers.ModelSerializer):
    class Meta:
        model = basic_models.ScoutOrgaLevel
        fields = '__all__'


class TagTypeLongSerializer(serializers.ModelSerializer):
    class Meta:
        model = basic_models.TagType
        fields = ('id',
                  'name',
                  'description',
                  'color')


class TagTypeShortSerializer(serializers.ModelSerializer):
    class Meta:
        model = basic_models.TagType
        fields = ('name',
                  'color')


class TagShortSerializer(serializers.ModelSerializer):
    type = TagTypeShortSerializer(many=False)

    class Meta:
        model = basic_models.Tag
        fields = ('id', 'name', 'type')


class TagLongSerializer(serializers.ModelSerializer):
    type = TagTypeLongSerializer(many=False)

    class Meta:
        model = basic_models.Tag
        fields = ('name',
                  'type',
                  'is_custom',
                  'is_visible',
                  'description')


class EatHabitSerializer(serializers.ModelSerializer):
    class Meta:
        model = basic_models.EatHabit
        fields = '__all__'


class FrontendThemeSerializer(serializers.ModelSerializer):
    class Meta:
        model = basic_models.FrontendTheme
        fields = '__all__'


class ZipCodeDetailedSerializer(serializers.ModelSerializer):
    class Meta:
        model = basic_models.ZipCode
        fields = ('zip_code', 'city', 'lat', 'lon')


class ScoutHierarchyDetailedSerializer(serializers.ModelSerializer):
    level = serializers.SlugRelatedField(
        many=False,
        read_only=True,
        slug_field='name'
    )
    zip_code = ZipCodeDetailedSerializer(many=False, read_only=True)
    ring = serializers.SerializerMethodField()
    bund = serializers.SerializerMethodField()
    stamm = serializers.SerializerMethodField()

    class Meta:
        model = basic_models.ScoutHierarchy
        fields = ('name', 'abbreviation', 'level', 'zip_code', 'ring', 'bund', 'stamm')

    def get_ring(self, obj: basic_models.ScoutHierarchy) -> str:
        return get_parent_scout_organisation(obj, 'Ring/Regional')

    def get_bund(self, obj: basic_models.ScoutHierarchy) -> str:
        return get_parent_scout_organisation(obj, 'Bund')

    def get_stamm(self, obj: basic_models.ScoutHierarchy) -> str:
        return get_parent_scout_organisation(obj, 'Stamm')


class DescriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = basic_models.Description
        exclude = ('public', 'type')
