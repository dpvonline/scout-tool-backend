from django.contrib.auth import get_user_model
from django.db.models.signals import pre_delete, post_save
from django.dispatch import receiver
from keycloak import KeycloakGetError
from notifications.signals import notify

from backend.settings import keycloak_admin
from .choices import RequestGroupAccessChoices
from .models import CustomUser, RequestGroupAccess

User: CustomUser = get_user_model()


@receiver(pre_delete, sender=CustomUser, dispatch_uid='pre_delete_user')
def pre_delete_user(sender, instance: CustomUser, **kwargs):
    delete_user_async(instance)


def delete_user_async(instance):
    if instance.keycloak_id:
        try:
            keycloak_user = keycloak_admin.get_user(instance.keycloak_id)

            # if keycloak_user['username'] == instance.username:
            #     keycloak_admin.delete_user(instance.keycloak_id)
            # else:
            #     print('shit')

        except KeycloakGetError:
            pass
        instance.person.delete()


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
def post_save_request_group_access(sender, instance: RequestGroupAccess, **kwargs):
    if not instance.pk or not instance.user:
        return

    in_group = False
    user_groups = keycloak_admin.get_user_groups(user_id=instance.user.keycloak_id)
    if any(d['id'] == instance.group.keycloak_id for d in user_groups):
        in_group = True

    if instance.status == RequestGroupAccessChoices.ACCEPTED:
        if not in_group:
            keycloak_admin.group_user_add(user_id=instance.user.keycloak_id, group_id=instance.group.keycloak_id)
    elif instance.status == RequestGroupAccessChoices.DECLINED:
        if in_group:
            keycloak_admin.group_user_remove(user_id=instance.user.keycloak_id, group_id=instance.group.keycloak_id)


@receiver(post_save, sender=RequestGroupAccess, dispatch_uid='request_group_access')
def request_group_access(sender, instance: RequestGroupAccess, created, **kwargs):
    if created:
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
            instance.user,
            recipient=recipients,
            verb='will .',
            target=instance.group
        )
