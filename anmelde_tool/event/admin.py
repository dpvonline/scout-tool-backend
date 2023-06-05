from django.contrib import admin

from anmelde_tool.event.models import EventLocation, Event, BookingOption, EventModule, StandardEventTemplate


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
    list_display = ('name', 'standard', 'event')
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
        return form
