from django.contrib.auth import get_user_model
from django.db.models.signals import post_save
from django.dispatch import receiver

from notifications.models import Notification

from authentication.models import CustomUser

User: CustomUser = get_user_model()


@receiver(post_save, sender=Notification, dispatch_uid='notification_created')
def notification_created(sender, instance: Notification, created, **kwargs):
    if created and not instance.emailed:
        pass
