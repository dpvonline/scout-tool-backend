from django.apps import AppConfig
from django.db.models.signals import pre_delete, post_save


class AuthenticationConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'authentication'

    def ready(self):
        from .signals import pre_delete_user, post_save_user
        from .models import CustomUser

        pre_delete.connect(pre_delete_user, sender=CustomUser, dispatch_uid="pre_delete_user")
        post_save.connect(post_save_user, sender=CustomUser, dispatch_uid="pre_delete_user")
