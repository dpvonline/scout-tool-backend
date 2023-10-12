from rest_framework import serializers
from basic import models as basic_models

"""
# noqa turn off pycharm warnings about missing abstract methods, which is a bug of pycharm
"""


def get_parent_scout_organisation(obj: basic_models.ScoutHierarchy, filter_level: str) -> str:
    if isinstance(obj, basic_models.ScoutHierarchy):
        iterator: basic_models.ScoutHierarchy = obj
        while iterator is not None:
            if iterator.level.name == filter_level:
                return iterator.name
            iterator = iterator.parent

    return ''

def get_parent_scout_organisation_by_id(obj: basic_models.ScoutHierarchy, filter_id: int) -> str:
    if isinstance(obj, basic_models.ScoutHierarchy):
        iterator: basic_models.ScoutHierarchy = obj
        while iterator is not None:
            if iterator.level.id == filter_id:
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
    display_name = serializers.SerializerMethodField()

    class Meta:
        model = basic_models.ScoutHierarchy
        fields = ('id', 'name', 'display_name', 'abbreviation', 'level',
                  'zip_code', 'ring', 'bund', 'stamm')

    def get_ring(self, obj: basic_models.ScoutHierarchy) -> str:
        return get_parent_scout_organisation(obj, 'Ring/Regional')

    def get_bund(self, obj: basic_models.ScoutHierarchy) -> str:
        return get_parent_scout_organisation(obj, 'Bund')

    def get_stamm(self, obj: basic_models.ScoutHierarchy) -> str:
        return get_parent_scout_organisation(obj, 'Stamm')

    def get_display_name(self, obj: basic_models.ScoutHierarchy) -> str:
        display_parent_id = obj.level.id - 1

        # handle Ringe as Bund
        display_parent_id_2 = display_parent_id if display_parent_id != 4 else 3

        display_parent_name = get_parent_scout_organisation_by_id(obj, display_parent_id_2)
        return f"{obj.name} ({display_parent_name})"


class DescriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = basic_models.Description
        exclude = ('public', 'type')


class CheckZipCodeSerializer(serializers.Serializer):  # noqa
    zip_code = serializers.CharField(required=True)
