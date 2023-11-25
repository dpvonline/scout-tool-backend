from django.contrib import admin
from django.db.models import F, Value, CharField
from django.db.models.functions import Concat

from .models import ScoutHierarchy, ZipCode, ScoutOrgaLevel, TagType, Tag, Description, EatHabit, FrontendTheme

admin.site.register(ScoutOrgaLevel)
admin.site.register(Description)
admin.site.register(FrontendTheme)


@admin.register(EatHabit)
class EatHabitAdmin(admin.ModelAdmin):
    def get_participants(self, obj: EatHabit):
        participants = obj.registrationparticipant_set.all()[:5].values(
            full_name=Concat(F('first_name'), Value(' '), F('last_name'), Value(' ('), F('registration__event__name'),
                             Value(')'), output_field=CharField()))
        list_names = [participant['full_name'] for participant in participants]
        return ', '.join(list_names)

    list_display = ('name', 'get_participants')
    search_fields = ('name',)


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'type')
    search_fields = ('name',)
    autocomplete_fields = ('type',)


@admin.register(ScoutHierarchy)
class ScoutHierarchyAdmin(admin.ModelAdmin):
    list_display = ('name', 'level', 'zip_code', 'parent')
    list_filter = ('level',)
    search_fields = ('name', 'zip_code__zip_code', 'zip_code__city', 'abbreviation', 'id', 'keycloak__id', 'keycloak__keycloak_id')
    ordering = ('name',)
    autocomplete_fields = ('keycloak',)


@admin.register(ZipCode)
class ZipCodeAdmin(admin.ModelAdmin):
    list_display = ('zip_code', 'city')
    search_fields = ('zip_code', 'city')


@admin.register(TagType)
class TagTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'color')
    search_fields = ('name',)
