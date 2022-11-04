from django.contrib import admin

from .models import KeycloakGroup, KeycloakRole

admin.site.register(KeycloakRole)


@admin.register(KeycloakGroup)
class RequestGroupAccessAdmin(admin.ModelAdmin):
    autocomplete_fields = ('parent',)
    search_fields = ('name', 'keycloak_id')
