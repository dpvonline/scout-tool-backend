from colorfield.fields import ColorField
from django.db import models

from basic.choices import DescriptionType, StateChoices, ScoutOrganisationLevelChoices


class TimeStampMixin(models.Model):
    created_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, blank=True, null=True)

    class Meta:
        abstract = True


class ZipCode(TimeStampMixin):
    id = models.AutoField(auto_created=True, primary_key=True)
    zip_code = models.CharField(max_length=5, blank=True)
    city = models.CharField(max_length=60, blank=True)
    lat = models.DecimalField(max_digits=20, decimal_places=15, default=0.000)
    lon = models.DecimalField(max_digits=20, decimal_places=15, default=0.000)
    state = models.CharField(max_length=2, choices=StateChoices.choices, default=StateChoices.BY)

    def __str__(self):
        return f"{self.zip_code} {self.city}"


class TagType(models.Model):
    id = models.AutoField(auto_created=True, primary_key=True)
    name = models.CharField(max_length=100, blank=True)
    description = models.CharField(max_length=100, blank=True)
    color = ColorField(default='#FF0000')
    min = models.IntegerField(default=0)
    max = models.IntegerField(default=9999)

    def __str__(self):
        return self.name


class Tag(models.Model):
    id = models.AutoField(auto_created=True, primary_key=True)
    name = models.CharField(max_length=100, blank=True)
    type = models.ForeignKey(TagType, null=True, blank=False, on_delete=models.PROTECT)
    is_custom = models.BooleanField(default=False)
    is_visible = models.BooleanField(default=True)

    def __str__(self):
        return f'{self.type}: {self.name}'


class ScoutOrgaLevel(TimeStampMixin):
    id = models.AutoField(auto_created=True, primary_key=True)
    name = models.CharField(max_length=20)
    description = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return self.name


class ScoutHierarchy(TimeStampMixin):
    id = models.AutoField(auto_created=True, primary_key=True)
    level = models.ForeignKey(ScoutOrgaLevel, on_delete=models.PROTECT, null=True, blank=True)
    level_choice = models.CharField(
        max_length=10,
        choices=ScoutOrganisationLevelChoices.choices,
        default=ScoutOrganisationLevelChoices.GRUPPE
    )
    name = models.CharField(max_length=60, blank=True)
    zip_code = models.ForeignKey(ZipCode, on_delete=models.PROTECT, null=True, blank=True)
    parent = models.ForeignKey('self', null=True, on_delete=models.PROTECT, related_name='scouthierarchy', blank=True)
    abbreviation = models.CharField(max_length=5, blank=True, null=True)
    keycloak_id = models.CharField(max_length=100, blank=True, null=True)

    def __generate_tree_name(self, lower: bool = True) -> str:
        if lower:
            name = self.name.lower()
            seperator = '_'
        else:
            name = self.name
            seperator = '/'

        if self.parent:
            return f'{self.parent.__generate_tree_name(lower)}{seperator}{name}'
        else:
            return name

    @property
    def keycloak_role_name(self) -> str:
        return f'{self.__generate_tree_name(lower=True)}_role'

    def generate_group_tree(self):
        level_dict = {
            3: 'Bünde',
            4: 'Ringe',
            5: 'Stämme'
        }
        if self.parent:
            return f'{self.parent.generate_group_tree()}/{level_dict[self.level.id]}/{self.name}'
        else:
            return self.name

    @property
    def keycloak_group_name(self) -> str:
        return f'/{self.generate_group_tree()}'

    @property
    def children(self):
        return ScoutHierarchy.objects.filter(parent=self.id)

    def __str__(self):
        return f"{self.level} - {self.name}"


class Description(TimeStampMixin):
    id = models.AutoField(auto_created=True, primary_key=True)
    public = models.BooleanField(default=False)
    question = models.TextField(max_length=250, null=True, blank=True)
    answer = models.TextField(max_length=10000, null=True, blank=True)
    type = models.CharField(max_length=3, choices=DescriptionType.choices, default=DescriptionType.FAQ)

    def __str__(self):
        return f'{self.get_type_display()}: {self.question}'


class EatHabit(models.Model):
    id = models.AutoField(auto_created=True, primary_key=True)
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class FrontendTheme(models.Model):
    id = models.AutoField(auto_created=True, primary_key=True)
    name = models.CharField(max_length=100, default='default')
    primary = ColorField(default='#1976D2')
    secondary = ColorField(default='#424242')
    accent = ColorField(default='#82B1FF')
    error = ColorField(default='#FF5252')
    info = ColorField(default='#2196F3')
    success = ColorField(default='#4CAF50')
    warning = ColorField(default='#FFC107')

    def __str__(self):
        return self.name
