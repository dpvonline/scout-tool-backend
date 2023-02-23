from celery import shared_task
from celery.utils.log import get_task_logger
from django.contrib.auth import get_user_model
from django.db.models.signals import post_save
from django.dispatch import receiver
from notifications.signals import notify

from authentication.models import CustomUser
from messaging.models import Issue

User: CustomUser = get_user_model()

logger = get_task_logger(__name__)


@receiver(post_save, sender=Issue, dispatch_uid='pre_delete_user')
def post_save_issue(sender, instance: Issue, **kwargs):
    try:
        post_save_issue.delay(instance.id)
    except:
        pass


@shared_task
def delete_keycloak_user_async(issue_id):
    if not issue_id:
        return

    issue = Issue.objects.get(id=issue_id)

    if not issue:
        return

    notify.send(
        sender=issue.created_by,
        recipient=issue.processors,
        verb=f'Dir wurde ein neue Anfrage zugewiesen.',
        target=Issue,
    )
