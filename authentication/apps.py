from django.apps import AppConfig
from django.db.models.signals import pre_delete, post_save


class AuthenticationConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'authentication'

    def ready(self):
        from .signals import pre_delete_user, post_save_user, post_save_request_group_access
        from .models import CustomUser, RequestGroupAccess

        pre_delete.connect(pre_delete_user, sender=CustomUser, dispatch_uid='pre_delete_user')
        post_save.connect(post_save_user, sender=CustomUser, dispatch_uid='post_save_user')
        post_save.connect(
            post_save_request_group_access,
            sender=RequestGroupAccess,
            dispatch_uid='post_save_request_group_access'
            )
