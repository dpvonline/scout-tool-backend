from django.core.management.base import BaseCommand
from keycloak import KeycloakAdmin
from keycloak_auth.models import KeycloakGroup
from backend.settings import env


class Command(BaseCommand):
    help = 'check keycloak groups'

    def __init__(self, stdout=None, stderr=None, no_color=False, force_color=False):
        super(Command, self).__init__(stdout, stderr, no_color, force_color)
        self.keycloak_admin = KeycloakAdmin(
            server_url=env('BASE_URI'),
            client_id=env('KEYCLOAK_ADMIN_USER'),
            client_secret_key=env('KEYCLOAK_ADMIN_PASSWORD'),
            realm_name=env('KEYCLOAK_APP_REALM'),
            user_realm_name=env('KEYCLOAK_APP_REALM'),
            verify=True
        )
        self.groups = {}

    def handle(self, *args, **options):
        all_groups = self.keycloak_admin.get_groups()

        for group in all_groups:
            self.get_subgroup(group)

    def get_subgroup(self, group, parent: KeycloakGroup = None):
        keycloak_group: KeycloakGroup = KeycloakGroup.objects.filter(keycloak_id=group['id'])
        if not keycloak_group.exists():
            keycloak_group = KeycloakGroup.objects.create(
                keycloak_id=group['id'],
                name=group['name'],
                parent=parent
            )
        elif keycloak_group.name != group['name']:
            keycloak_group.name = group['name']
            keycloak_group.save()

        if keycloak_group.parent is None or keycloak_group.parent != parent:
            keycloak_group.parent = parent
            keycloak_group.save()

        for sub_group in group['subGroups']:
            self.get_subgroup(sub_group, keycloak_group)
