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
    list_display = ('username',)
    search_fields = ('username', 'email')


@admin.register(Person)
class PersonAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'scout_group')
    autocomplete_fields = ('created_by', 'scout_group')


@admin.register(RequestGroupAccess)
class RequestGroupAccessAdmin(admin.ModelAdmin):
    autocomplete_fields = ('user', 'group')
