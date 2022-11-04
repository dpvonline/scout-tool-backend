from keycloak import KeycloakGetError

from backend.settings import keycloak_admin
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
    if instance.pk and instance.keycloak_id:
        keycloak_user = keycloak_admin.get_user(instance.keycloak_id)

        if keycloak_user['username'] == instance.username:
            scout_organisation = instance.scout_organisation and instance.scout_organisation.name

            keycloak_admin.update_user(
                instance.keycloak_id, {
                    'email': instance.email,
                    'firstName': instance.first_name,
                    'lastName': instance.last_name,
                    # 'attributes': {
                    #     'verband': '',
                    #     'fahrtenname': instance.scout_name,
                    #     'bund': '',
                    #     'stamm': scout_organisation
                    # }
                }
            )


def post_save_request_group_access(sender, instance: RequestGroupAccess, **kwargs):
    if not instance.pk:
        return
    if instance.accepted and instance.declined:
        return

    in_group = False
    user_groups = keycloak_admin.get_user_groups(user_id=instance.user.keycloak_id)
    if any(d['id'] == instance.group.keycloak_id for d in user_groups):
        in_group = True
    if instance.accepted:
        if not in_group:
            keycloak_admin.group_user_add(user_id=instance.user.keycloak_id, group_id=instance.group.keycloak_id)
    elif instance.declined:
        if in_group:
            keycloak_admin.group_user_remove(user_id=instance.user.keycloak_id, group_id=instance.group.keycloak_id)
