from django.contrib import admin

from .models import KeycloakGroup, KeycloakRole

admin.site.register(KeycloakGroup)
admin.site.register(KeycloakRole)
