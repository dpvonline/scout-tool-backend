from django.contrib import admin
from django.contrib.admin import display

from anmelde_tool.registration.models import Registration, RegistrationParticipant


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
