from django.contrib import admin

from .models import CustomUser, RequestGroupAccess
from .models import Person


# admin.site.register(CustomUser, UserAdmin)


@admin.register(CustomUser)
class UserAdmin(admin.ModelAdmin):
    """
    Admin class for the user extended model for database functionalities
    """
    list_display = ('username', 'email')
    search_fields = ('username', 'email', 'keycloak_id')


@admin.register(Person)
class PersonAdmin(admin.ModelAdmin):
    list_display = ('user', 'first_name', 'last_name', 'scout_group')
    autocomplete_fields = ('created_by', 'scout_group')


@admin.register(RequestGroupAccess)
class RequestGroupAccessAdmin(admin.ModelAdmin):
    autocomplete_fields = ('user', 'group')
    list_display = ('user', 'group', 'status', 'checked_by')
