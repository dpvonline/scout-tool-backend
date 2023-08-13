from django.core.management.base import BaseCommand
from django.shortcuts import get_object_or_404
from keycloak import KeycloakGetError

from backend.settings import keycloak_admin
from basic.choices import ScoutOrganisationLevelChoices
from basic.models import ScoutHierarchy
from keycloak_auth.helper import get_or_create_keycloak_model
from keycloak_auth.models import KeycloakGroup

additional_level_groups = {
    str(ScoutOrganisationLevelChoices.BUND): ['Bundesführung', 'Stellv. Bundesführung', 'Schatzamt'],
    str(ScoutOrganisationLevelChoices.RING): ['Ringführung', 'Stellv. Ringführung', 'Schatzamt'],
    str(ScoutOrganisationLevelChoices.STAMM): ['Stammesführung', 'Stellv. Stammesführung', 'Schatzamt'],
    str(ScoutOrganisationLevelChoices.VERBAND): ['Vorstand', ],
}


class Command(BaseCommand):
    help = 'check keycloak groups'

    def __init__(self, stdout=None, stderr=None, no_color=False, force_color=False):
        super(Command, self).__init__(stdout, stderr, no_color, force_color)
        self.groups_added = []

    def handle(self, *args, **options):

        print('checking existing keycloak groups')
        all_groups = keycloak_admin.get_groups()
        for group in all_groups:
            self.get_subgroup(group)

        print('creating missing scout hierarchies in keycloak')
        heads = ScoutHierarchy.objects.all()
        for head in heads:
            self.recursive_group_initialisation(head)

        if self.groups_added:
            print('')
            print('added groups:')
            for group in self.groups_added:
                print(group)

        print('Checks completed')

    def recursive_group_initialisation(self, head: ScoutHierarchy, add_children: bool = True) -> None:
        initialized = False
        group = None

        if head.keycloak and head.keycloak.keycloak_id:
            group, initialized = self.get_keycloak_group(head.keycloak.keycloak_id, head)

        if not initialized:
            group = keycloak_admin.get_group_by_path(path=head.keycloak_group_name, search_in_subgroups=True)
            if group:
                initialized = True

        if not initialized:
            parent_id: str | None = None

            if head.parent:
                parent_special_path = f'{head.parent.keycloak_group_name}/' \
                                      f'{ScoutOrganisationLevelChoices.get_level_choice_plural(head.level_choice)}'
                parent = keycloak_admin.get_group_by_path(path=parent_special_path, search_in_subgroups=True)
                if parent:
                    parent_id = parent['id']
                else:
                    self.recursive_group_initialisation(head.parent, add_children=False)
                    parent = keycloak_admin.get_group_by_path(path=parent_special_path, search_in_subgroups=True)
                    if parent:
                        parent_id = parent['id']
                    else:
                        parent_normal_path = head.parent.keycloak_group_name
                        parent_normal = keycloak_admin.get_group_by_path(
                            path=parent_normal_path,
                            search_in_subgroups=True
                        )
                        if parent_normal:
                            new_group_name = ScoutOrganisationLevelChoices.get_level_choice_plural(head.level_choice)
                            parent_id = self.create_keycloak_group(new_group_name, parent_normal['id'])
                            parent_group = keycloak_admin.get_group(parent_id)
                            get_or_create_keycloak_model(parent_group, parent_normal['id'])

            child_group = self.create_keycloak_group(head.name, parent_id, head.level_choice)

            group = keycloak_admin.get_group(group_id=child_group)

            self.groups_added.append(head.name)

            if not head.keycloak or head.keycloak.keycloak_id != group['id']:
                head.keycloak, _ = get_or_create_keycloak_model(group, parent_id)
                head.save()

        if not group:
            raise Exception('No group created or found')

        if add_children:
            for child in head.children:
                self.recursive_group_initialisation(child)

    def create_keycloak_group(self,
                              group_name: str,
                              parent_id: str | None = None,
                              level: str = None) -> str:
        payload = {'name': group_name}
        if parent_id:
            new_group_id = keycloak_admin.create_group(payload=payload, parent=parent_id)
        else:
            new_group_id = keycloak_admin.create_group(payload=payload)

        group = keycloak_admin.get_group(new_group_id)

        if level:
            view_role, admin_role = keycloak_admin.add_group_permissions(group, False)

            if level == str(ScoutOrganisationLevelChoices.STAMM):
                keycloak_admin.assign_group_client_roles(
                    new_group_id, keycloak_admin.realm_management_client_id,
                    [view_role]
                )

            extra_groups = additional_level_groups[level]
            for extra_group_name in extra_groups:
                extra_group_payload = {'name': extra_group_name}
                extra_group_id = keycloak_admin.create_group(payload=extra_group_payload, parent=new_group_id)
                extra_group = keycloak_admin.get_group(extra_group_id)
                keycloak_admin.assign_group_client_roles(
                    extra_group_id, keycloak_admin.realm_management_client_id,
                    [admin_role]
                )
                keycloak_admin.add_group_permissions(extra_group, True)
        return new_group_id

    def get_keycloak_group(self, keycloak_id, head) -> [dict, bool]:
        try:
            group = keycloak_admin.get_group(group_id=keycloak_id)
        except KeycloakGetError:
            pass
        else:
            if group and group['name'] == head.name:
                return group, True
        return None, False

    def get_subgroup(self, group, parent: KeycloakGroup | str = None):
        keycloak_group, created = get_or_create_keycloak_model(group, parent)

        if keycloak_group.name != group['name']:
            keycloak_group.name = group['name']
            keycloak_group.save()

        if keycloak_group.parent is None or keycloak_group.parent != parent:
            keycloak_group.parent = parent
            keycloak_group.save()

        # keycloak_admin.add_group_permissions(group, True)

        for sub_group in group['subGroups']:
            self.get_subgroup(sub_group, keycloak_group)
