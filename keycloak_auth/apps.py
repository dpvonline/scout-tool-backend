from django.apps import AppConfig


class KeycloakAuthConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'keycloak_auth'

    def ready(self):
        import keycloak_auth.signals
