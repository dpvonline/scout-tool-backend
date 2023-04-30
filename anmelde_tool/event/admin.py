from django.contrib import admin
from django.contrib.admin import display

from anmelde_tool.event.models import EventLocation, Event, BookingOption, EventModule, AttributeEventModuleMapper, \
    StandardEventTemplate, Registration, RegistrationParticipant, \
    Workshop, WorkshopParticipant

admin.site.register(Workshop)
admin.site.register(WorkshopParticipant)


@admin.register(EventLocation)
class EventLocationAdmin(admin.ModelAdmin):
    list_display = ('name', 'zip_code')
    search_fields = ('name',)
    autocomplete_fields = ('zip_code',)


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ('name', 'location', 'is_public')
    search_fields = ('name', 'location__name', 'id')
    autocomplete_fields = ('responsible_persons', 'invited_groups')


@admin.register(BookingOption)
class BookingOptionAdmin(admin.ModelAdmin):
    list_display = ('name', 'event')
    search_fields = ('name',)
    autocomplete_fields = ('event',)


@admin.register(EventModule)
class EventModuleAdmin(admin.ModelAdmin):
    list_display = ('name', 'standard')
    search_fields = ('name', 'id')
    list_filter = ('standard', 'event')


@admin.register(StandardEventTemplate)
class StandardEventTemplateAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('event', 'name')

    def get_form(self, request, obj=None, **kwargs):
        form = super(StandardEventTemplateAdmin, self).get_form(request, obj, **kwargs)
        form.base_fields['introduction'].queryset = EventModule.objects.exclude(standard=False)
        form.base_fields['summary'].queryset = EventModule.objects.exclude(standard=False)
        form.base_fields['participants'].queryset = EventModule.objects.exclude(standard=False)
        form.base_fields['letter'].queryset = EventModule.objects.exclude(standard=False)
        form.base_fields['other_required_modules'].queryset = EventModule.objects.exclude(standard=False)
        form.base_fields['other_optional_modules'].queryset = EventModule.objects.exclude(standard=False)
        return form


@admin.register(Registration)
class RegistrationAdmin(admin.ModelAdmin):
    list_display = ('scout_organisation', 'get_event_name', 'is_confirmed')
    search_fields = ('scout_organisation__name',)
    autocomplete_fields = ('event', 'scout_organisation')
    list_filter = ('event__name',)

    @display(ordering='event__name', description='Event name')
    def get_event_name(self, obj):
        return obj.event.name


@admin.register(RegistrationParticipant)
class RegistrationParticipantAdmin(admin.ModelAdmin):
    list_display = (
        'registration',
        'first_name',
        'last_name',
        'scout_name',
        'generated',
    )
    list_filter = ('registration__event__name', 'registration__scout_organisation__name')
    search_fields = ('scout_name', 'first_name', 'last_name', 'email')
    autocomplete_fields = ('zip_code', 'scout_group')
