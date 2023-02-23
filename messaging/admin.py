from django.contrib import admin

from messaging.models import Message, IssueType, Issue

admin.site.register(Message)


@admin.register(IssueType)
class IssueTypeAdmin(admin.ModelAdmin):
    autocomplete_fields = ('responsable_groups',)


class MessageInline(admin.TabularInline):
    model = Message


@admin.register(Issue)
class PackageAdmin(admin.ModelAdmin):
    inlines = [
        MessageInline,
    ]
