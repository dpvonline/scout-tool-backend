from celery import shared_task
from celery.utils.log import get_task_logger
from django.contrib.auth import get_user_model
from django.db.models.signals import post_save
from django.dispatch import receiver
from notifications.signals import notify

from authentication.models import CustomUser
from backend.settings import keycloak_admin
from messaging.models import Issue

User: CustomUser = get_user_model()

logger = get_task_logger(__name__)


@receiver(post_save, sender=Issue, dispatch_uid='pre_delete_user')
def post_save_issue(sender, instance: Issue, **kwargs):
    try:
        create_notification_issue.delay(instance.id)
    except:
        pass


@shared_task
def create_notification_issue(issue_id):
    if not issue_id:
        return

    issue = Issue.objects.get(id=issue_id)

    if not issue:
        return

    recipients_ids = []
    for keycloak_group in issue.issue_type.responsable_groups.all():
        user = keycloak_admin.get_group_members(
            keycloak_group.keycloak_id,
            {"briefRepresentation": True}
        )
        recipients_ids.extend([val['id'] for val in user])

    recipients = User.objects.filter(keycloak_id__in=recipients_ids)

    if issue.created_by:
        sender = issue.created_by
    else:
        sender = User.objects.filter(username='admin').first()

    notify.send(
        sender=sender,
        recipient=recipients,
        verb=f'Dir wurde ein neue Anfrage zugewiesen.',
        target=issue,
    )
