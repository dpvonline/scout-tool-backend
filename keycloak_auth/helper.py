import re
import logging

from django.db.models import QuerySet
from keycloak import KeycloakGetError, KeycloakAuthenticationError

from backend.settings import keycloak_user
from keycloak_auth.api_exceptions import NotAuthorized
from keycloak_auth.models import KeycloakGroup

REGEX_GROUP = re.compile('[a-z0-9]{8}-[a-z0-9]{4}-[a-z0-9]{4}-[a-z0-9]{4}-[a-z0-9]{12}')
REGEX_GROUP_ADMIN_PERMISSION = re.compile(
    'group-[a-z0-9]{8}-[a-z0-9]{4}-[a-z0-9]{4}-[a-z0-9]{4}-[a-z0-9]{12}-admin-role'
)

logger = logging.getLogger(__name__)

def get_or_create_keycloak_model(group: dict, parent_obj: str | KeycloakGroup) -> tuple[KeycloakGroup, bool]:
    if isinstance(parent_obj, KeycloakGroup):
        parent = parent_obj
    elif isinstance(parent_obj, str):
        parent = KeycloakGroup.objects.filter(keycloak_id=parent_obj).first()
    else:
        parent = None

    keycloak_groups: QuerySet[KeycloakGroup] = KeycloakGroup.objects.filter(keycloak_id=group['id'])
    if not keycloak_groups.exists():
        keycloak_group = KeycloakGroup.objects.create(
            keycloak_id=group['id'],
            name=group['name'],
            parent=parent
        )
        return keycloak_group, True
    else:
        if keycloak_groups.count() > 1:
            print('ERROR')
            raise Exception('Multiple keycloak groups found, error in data, please fix manually')
        else:
            return keycloak_groups.first(), False


def check_group_id(group_id: str) -> bool:
    if REGEX_GROUP.match(group_id):
        return True
    return False


def check_group_admin_permission(group_id: str) -> bool:
    if REGEX_GROUP_ADMIN_PERMISSION.match(group_id):
        return True
    return False


def get_groups_of_user(token,keycloak_id):
    try:
        keycloak_groups = keycloak_user.get_user_groups(
            token,
            keycloak_id,
            brief_representation=True
        )
    except KeycloakGetError as err:
        logger.exception(err)
        raise NotAuthorized()
    except KeycloakAuthenticationError:
        raise NotAuthorized()

    ids = [val['id'] for val in keycloak_groups]
    return ids
