from .models import CustomUser
from backend.settings import keycloak_admin


def pre_delete_user(sender, instance: CustomUser, **kwargs):
    delete_user_async(instance)


def delete_user_async(instance):
    if instance.keycloak_id:
        keycloak_user = keycloak_admin.get_user(instance.keycloak_id)

        if keycloak_user['username'] == instance.username:
            keycloak_admin.delete_user(instance.keycloak_id)
        else:
            print('shit')


def post_save_user(sender, instance: CustomUser, **kwargs):
    if instance.pk and instance.keycloak_id:
        keycloak_user = keycloak_admin.get_user(instance.keycloak_id)

        if keycloak_user['username'] == instance.username:
            scout_organisation = instance.scout_organisation and instance.scout_organisation.name

            keycloak_admin.update_user(instance.keycloak_id, {
                'email': instance.email,
                'firstName': instance.first_name,
                'lastName': instance.last_name,
                # 'attributes': {
                #     'verband': '',
                #     'fahrtenname': instance.scout_name,
                #     'bund': '',
                #     'stamm': scout_organisation
                # }
            })
