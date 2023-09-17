from django.core.management.base import BaseCommand

from basic.helper.sync_keycloak_groups import SyncKeycloakGroups


class Command(BaseCommand):
    help = 'check keycloak groups'

    def handle(self, *args, **options):
        SyncKeycloakGroups().run()
