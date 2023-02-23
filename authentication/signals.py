from celery import shared_task
from celery.utils.log import get_task_logger
from django.contrib.auth import get_user_model
from django.db.models.signals import pre_delete, post_save
from django.dispatch import receiver
from keycloak import KeycloakGetError
from notifications.signals import notify

from authentication.custom_notifications.email_services import instant_notification
from backend.settings import keycloak_admin
from .choices import RequestGroupAccessChoices
from .models import CustomUser, RequestGroupAccess

User: CustomUser = get_user_model()

logger = get_task_logger(__name__)


@receiver(pre_delete, sender=CustomUser, dispatch_uid='pre_delete_user')
def pre_delete_user(sender, instance: CustomUser, **kwargs):
    try:
        instance.person.delete()
    except:
        pass
    try:
        delete_keycloak_user_async.delay(instance.keycloak_id, instance.username)
    except:
        pass


@shared_task
def delete_keycloak_user_async(keycloak_id, username):
    if keycloak_id:
        try:
            keycloak_user = keycloak_admin.get_user(keycloak_id)

            if keycloak_user['username'] == username:
                keycloak_admin.delete_user(keycloak_id)
            else:
                print('shit')

        except KeycloakGetError:
            pass


@receiver(post_save, sender=CustomUser, dispatch_uid='post_save_user')
def post_save_user(sender, instance: CustomUser, **kwargs):
    if not instance.pk or not instance.keycloak_id or not hasattr(instance, 'person'):
        return
    keycloak_user = keycloak_admin.get_user(instance.keycloak_id)

    if keycloak_user['username'] == instance.username:
        scout_organisation = instance.person.scout_group and instance.person.scout_group.name
        keycloak_admin.update_user(
            instance.keycloak_id, {
                'email': instance.email,
                'firstName': instance.person.first_name,
                'lastName': instance.person.last_name,
                'attributes': {
                    'verband': 'DPV',
                    'fahrtenname': instance.person.scout_name,
                    'bund': '',
                    'stamm': scout_organisation
                }
            }
        )


@receiver(post_save, sender=RequestGroupAccess, dispatch_uid='post_save_request_group_access')
def post_save_request_group_access(sender, instance: RequestGroupAccess, created, **kwargs):
    if not instance.pk or not instance.user:
        return

    if created:
        create_notification_async.delay(instance.id)
    else:
        move_user_into_group.delay(instance.id)


@shared_task
def move_user_into_group(instance_pk):
    instance = RequestGroupAccess.objects.get(id=instance_pk)

    in_group = False
    user_groups = keycloak_admin.get_user_groups(user_id=instance.user.keycloak_id)
    if any(d['id'] == instance.group.keycloak_id for d in user_groups):
        in_group = True
    decision = ''
    if instance.status == RequestGroupAccessChoices.ACCEPTED:
        if not in_group:
            keycloak_admin.group_user_add(user_id=instance.user.keycloak_id, group_id=instance.group.keycloak_id)
        decision = 'angenommen'
    elif instance.status == RequestGroupAccessChoices.DECLINED:
        if in_group:
            keycloak_admin.group_user_remove(user_id=instance.user.keycloak_id, group_id=instance.group.keycloak_id)
        decision = 'abgelehnt'

    notify.send(
        sender=instance.checked_by,
        recipient=instance.user,
        verb=f'Deine Gruppenanfrage wurde {decision}',
        target=instance.RequestGroupAccess,
    )


@shared_task
def create_notification_async(instance_pk):
    instance = RequestGroupAccess.objects.get(id=instance_pk)
    admin_name = f'group-{instance.group.keycloak_id}-admin-role'
    all_group_recipients = keycloak_admin.get_client_role_groups(
        keycloak_admin.realm_management_client_id,
        admin_name
    )
    all_user_recipients = keycloak_admin.get_client_role_members(
        keycloak_admin.realm_management_client_id,
        admin_name
    )
    recipient_ids = [val['id'] for val in all_user_recipients if val['enabled']]
    for group_recipient in all_group_recipients:
        group_members = keycloak_admin.get_group_members(group_recipient['id'])
        recipient_ids += [val['id'] for val in group_members if val['enabled']]
    recipients = User.objects.filter(keycloak_id__in=recipient_ids)
    if recipients.count() == 0:
        recipients = User.objects.filter(is_staff=True)
    notify.send(
        sender=instance.user,
        recipient=recipients,
        verb=f'möchte gerne in der Gruppe aufgenommen werden.',
        target=instance.group,
    )
    ids = list(recipients.values_list('id', flat=True))
    instant_notification.delay(ids)
