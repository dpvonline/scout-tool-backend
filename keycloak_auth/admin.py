from django.contrib import admin

from .models import KeycloakGroup, ExternalLinks


@admin.register(KeycloakGroup)
class RequestGroupAccessAdmin(admin.ModelAdmin):
    autocomplete_fields = ('parent',)
    search_fields = ('name', 'keycloak_id','id')
    ordering = ('name',)


@admin.register(ExternalLinks)
class ExternalLinksAdmin(admin.ModelAdmin):
    autocomplete_fields = ('keycloak_group',)
    search_fields = ('keycloak_group__name', 'keycloak_group__keycloak_id')
