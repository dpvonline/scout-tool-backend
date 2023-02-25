from celery import shared_task
from celery.utils.log import get_task_logger
from django.contrib.auth import get_user_model
from django.db.models.signals import post_save
from django.dispatch import receiver
from notifications.signals import notify

from backend.settings import keycloak_admin
from .choices import RequestGroupAccessChoices
from .models import CustomUser, RequestGroupAccess, Person

User: CustomUser = get_user_model()

logger = get_task_logger(__name__)


# @receiver(pre_delete, sender=CustomUser, dispatch_uid='pre_delete_user')
# def pre_delete_user(sender, instance: CustomUser, **kwargs):
#     try:
#         instance.person.delete()
#     except:
#         pass
#     try:
#         delete_keycloak_user_async.delay(instance.keycloak_id, instance.username)
#     except:
#         pass


# @shared_task
# def delete_keycloak_user_async(keycloak_id, username):
# if keycloak_id:
#     try:
#         keycloak_user = keycloak_admin.get_user(keycloak_id)
#
#         if keycloak_user['username'] == username:
#             keycloak_admin.delete_user(keycloak_id)
#         else:
#             print('shit')
#
#     except KeycloakGetError:
#         pass


@receiver(post_save, sender=CustomUser, dispatch_uid='post_save_user')
def post_save_user(sender, instance: CustomUser, created, **kwargs):
    if not instance.keycloak_id and not created:
        return
    keycloak_user = keycloak_admin.get_user(instance.keycloak_id)

    if keycloak_user['username'] == instance.username:
        first_name = keycloak_user['firstName']
        last_name = keycloak_user['lastName']
        email = keycloak_user['email']

        if first_name != instance.first_name:
            first_name = instance.first_name

        if last_name != instance.last_name:
            last_name = instance.last_name

        if email != instance.email:
            email = instance.email

        keycloak_admin.update_user(
            instance.keycloak_id, {
                'email': email,
                'firstName': first_name,
                'lastName': last_name,
            }
        )


@receiver(post_save, sender=Person, dispatch_uid='post_save_person')
def post_save_person(sender, instance: Person, created, **kwargs):
    if not instance.user or not instance.user.keycloak_id and not created:
        return
    keycloak_user = keycloak_admin.get_user(instance.user.keycloak_id)

    if keycloak_user['username'] == instance.user.username:
        verband = keycloak_user['attributes'].get('verband')
        bund = keycloak_user['attributes'].get('bund')
        stamm = keycloak_user['attributes'].get('stamm')
        fahrtenname = keycloak_user['attributes'].get('fahrtenname')

        if verband:
            verband = verband[0]

        if bund:
            bund = bund[0]

        if fahrtenname:
            fahrtenname = fahrtenname[0]

        if stamm:
            stamm = stamm[0]

        if instance.scout_group and verband != instance.scout_group.verband:
            verband = instance.scout_group.verband

        if instance.scout_group and bund != instance.scout_group.bund:
            bund = instance.scout_group.bund

        if instance.scout_group and stamm != instance.scout_group.name:
            stamm = instance.scout_group.name

        if fahrtenname != instance.scout_name:
            fahrtenname = instance.scout_name

        keycloak_admin.update_user(
            instance.user.keycloak_id, {
                'attributes': {
                    'verband': verband,
                    'fahrtenname': fahrtenname,
                    'bund': bund,
                    'stamm': stamm
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
        target=instance,
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
        recipient_ids.extend([val['id'] for val in group_members if val['enabled']])

    recipients = User.objects.filter(keycloak_id__in=recipient_ids)
    if recipients.count() == 0:
        recipients = User.objects.filter(is_staff=True)
    notify.send(
        sender=instance.user,
        recipient=recipients,
        verb=f'möchte gerne in der Gruppe aufgenommen werden.',
        target=instance.group,
    )
