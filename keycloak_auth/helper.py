from keycloak_auth.models import KeycloakGroup


def get_or_create_keycloak_group(group: dict, parent_obj: str | KeycloakGroup | None) -> tuple[KeycloakGroup, bool]:
    if isinstance(parent_obj, KeycloakGroup):
        parent = parent_obj
    elif isinstance(parent_obj, str):
        parent = KeycloakGroup.objects.filter(keycloak_id=parent_obj).first()
    else:
        parent = None

    keycloak_groups: KeycloakGroup = KeycloakGroup.objects.filter(keycloak_id=group['id'])
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
