from .models import Person

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, RequestGroupAccess


# admin.site.register(CustomUser, UserAdmin)


@admin.register(CustomUser)
class UserAdmin(admin.ModelAdmin):
    """
    Admin class for the user extended model for database functionalities
    """
    list_display = ('username', 'scout_organisation')
    autocomplete_fields = ('scout_organisation',)
    search_fields = ('username', 'email')


@admin.register(Person)
class PersonAdmin(admin.ModelAdmin):
    autocomplete_fields = ('created_by',)


@admin.register(RequestGroupAccess)
class RequestGroupAccessAdmin(admin.ModelAdmin):
    autocomplete_fields = ('user', 'group')
