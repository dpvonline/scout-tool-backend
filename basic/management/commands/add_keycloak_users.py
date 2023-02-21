from django.core.management.base import BaseCommand
from authentication.sync_keycloak_users import import_keycloak_members


class Command(BaseCommand):
    help = 'add all fixtures'

    def handle(self, *args, **options):
        import_keycloak_members()
