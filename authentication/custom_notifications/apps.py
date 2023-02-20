from django.apps import AppConfig


class AuthenticationConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'authentication.custom_notifications'

    def ready(self):
        import authentication.custom_notifications.signals  # noqa
