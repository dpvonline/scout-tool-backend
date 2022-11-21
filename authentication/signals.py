from keycloak import KeycloakGetError

from backend.settings import keycloak_admin
from .choices import RequestGroupAccessChoices
from .models import CustomUser, RequestGroupAccess


def pre_delete_user(sender, instance: CustomUser, **kwargs):
    delete_user_async(instance)


def delete_user_async(instance):
    if instance.keycloak_id:
        try:
            keycloak_user = keycloak_admin.get_user(instance.keycloak_id)

            if keycloak_user['username'] == instance.username:
                keycloak_admin.delete_user(instance.keycloak_id)
            else:
                print('shit')

        except KeycloakGetError:
            pass


def post_save_user(sender, instance: CustomUser, **kwargs):
    if not instance.pk or not instance.keycloak_id or not hasattr(instance, 'person'):
        return
    # keycloak_user = keycloak_admin.get_user(instance.keycloak_id)
    #
    # if keycloak_user['username'] == instance.username:
    #     scout_organisation = instance.person.scout_group and instance.person.scout_group.name
    #     keycloak_admin.update_user(
    #         instance.keycloak_id, {
    #             'email': instance.email,
    #             'firstName': instance.person.first_name,
    #             'lastName': instance.person.last_name,
    #             'attributes': {
    #                 'verband': 'DPV',
    #                 'fahrtenname': instance.person.scout_name,
    #                 'bund': '',
    #                 'stamm': scout_organisation
    #             }
    #         }
    #     )


def post_save_request_group_access(sender, instance: RequestGroupAccess, **kwargs):
    if not instance.pk:
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
