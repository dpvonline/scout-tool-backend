import uuid

from django.db import models


class KeycloakRole(models.Model):
    id = models.UUIDField(auto_created=True, primary_key=True, default=uuid.uuid4, editable=False)
    keycloak_id = models.CharField(max_length=36)
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class KeycloakGroup(models.Model):
    id = models.UUIDField(auto_created=True, primary_key=True, default=uuid.uuid4, editable=False)
    keycloak_id = models.CharField(max_length=36, unique=True)
    name = models.CharField(max_length=100)
    roles = models.ManyToManyField(KeycloakRole, blank=True)
    parent = models.ForeignKey('self', null=True, on_delete=models.SET_NULL, related_name='keycloak_group', blank=True)

    def __str__(self):
        return self.name
