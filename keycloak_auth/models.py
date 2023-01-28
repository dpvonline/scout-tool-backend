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
    keycloak_id = models.CharField(max_length=36, unique=True, blank=True)
    name = models.CharField(max_length=100)
    roles = models.ManyToManyField(KeycloakRole, blank=True)
    parent = models.ForeignKey('self', null=True, on_delete=models.CASCADE, related_name='keycloak_group', blank=True)

    @property
    def children(self):
        return KeycloakGroup.objects.filter(parent=self.id)

    @property
    def keycloak_group_name(self) -> str:
        if self.parent:
            return f'{self.parent.keycloak_group_name}/{self.name}'
        else:
            return f'/{self.name}'

    def __str__(self):
        return self.name


class ExternalLinks(models.Model):
    id = models.AutoField(primary_key=True)
    wiki = models.URLField(blank=True, null=True)
    cloud = models.URLField(blank=True, null=True)
    keycloak_group = models.OneToOneField(KeycloakGroup, on_delete=models.CASCADE)

