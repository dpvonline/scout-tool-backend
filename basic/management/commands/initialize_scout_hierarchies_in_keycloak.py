from django.core.management.base import BaseCommand

from basic.helper.initialize_keycloak_scout_hierarchies import InitKeycloakScoutHierarchies


class Command(BaseCommand):
    help = 'check keycloak groups'

    def handle(self, *args, **options):
        InitKeycloakScoutHierarchies().run()


