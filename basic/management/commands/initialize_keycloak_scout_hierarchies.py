from django.core.management.base import BaseCommand
from keycloak import KeycloakGetError

from backend.settings import keycloak_admin
from basic.choices import ScoutOrganisationLevelChoices
from basic.models import ScoutHierarchy
from keycloak_auth.models import KeycloakGroup

additional_level_groups = {
    str(ScoutOrganisationLevelChoices.BUND): ['Bundesführung', 'Stellv. Bundesführung', 'Schatzamt'],
    str(ScoutOrganisationLevelChoices.RING): ['Ringführung', 'Stellv. Ringführung', 'Schatzamt'],
    str(ScoutOrganisationLevelChoices.STAMM): ['Stammesführung', 'Stellv. Stammesführung', 'Schatzamt'],
}


class Command(BaseCommand):
    help = 'check keycloak groups'

    def __init__(self, stdout=None, stderr=None, no_color=False, force_color=False):
        super(Command, self).__init__(stdout, stderr, no_color, force_color)
        self.groups_added = []

    def handle(self, *args, **options):
        all_groups = keycloak_admin.get_groups()

        # for group in all_groups:
        #     self.get_subgroup(group)

        heads = ScoutHierarchy.objects.filter(name='PB-Nordlicht')

        for head in heads:
            self.recursive_group_initialisation(head)

        if self.groups_added:
            print('')
            print('added groups:')
            for group in self.groups_added:
                print(group)

        print('Checks completed')

    def get_subgroup(self, group):
        # keycloak_admin.add_group_permissions(group=group)
        for sub_group in group['subGroups']:
            if sub_group['subGroups']:
                self.get_subgroup(sub_group)

    def recursive_group_initialisation(self, head: ScoutHierarchy, keycloak_parent: str = None):
        print(f'{head=}')
        initialized = False
        group = None

        if head.keycloak.keycloak_id:
            group, initialized = self.get_keycloak_group(group, head)

        if not initialized:
            group = keycloak_admin.get_group_by_path(path=head.keycloak_group_name, search_in_subgroups=True)
            if group:
                initialized = True

        if not initialized:
            parent_id = None

            if head.parent:
                parent = None
                if keycloak_parent:
                    parent_group, parent_found = self.get_keycloak_group(keycloak_parent, head.parent)
                    print(f'{parent_group=}, {parent_found=}')
                    if parent_found:
                        parent = keycloak_parent
                        parent_id = parent['id']
                else:
                    parent_special_path = f'{head.parent.keycloak_group_name}/' \
                                          f'{ScoutOrganisationLevelChoices.get_level_choice_plural(head.level_choice)}'
                    print(f'{parent_special_path=}')
                    parent = keycloak_admin.get_group_by_path(path=parent_special_path, search_in_subgroups=True)

                if parent:
                    parent_id = parent['id']
                else:
                    parent_normal_path = head.parent.keycloak_group_name
                    parent_normal = keycloak_admin.get_group_by_path(
                        path=parent_normal_path,
                        search_in_subgroups=True
                    )
                    print(f'{parent_normal_path=}')
                    if parent_normal:
                        parent_normal_id = parent_normal['id']
                        payload = {'name': ScoutOrganisationLevelChoices.get_level_choice_plural(head.level_choice)}
                        parent_special = keycloak_admin.create_group(payload=payload, parent=parent_normal_id)
                        parent_id = parent_special

            payload = {'name': head.name}
            if parent_id:
                print(f'{payload=}, {parent_id=}')
                child_group = keycloak_admin.create_group(payload=payload, parent=parent_id)
            else:
                child_group = keycloak_admin.create_group(payload=payload)

            group = keycloak_admin.get_group(group_id=child_group)

            self.groups_added.append(head.name)

            if not head.keycloak:
                keycloak_group = keycloak_admin.get_group_by_path(
                    path=head.keycloak_group_name,
                    search_in_subgroups=True
                )
                django_keycloak_group = KeycloakGroup.objects.get(keycloak_id=keycloak_group['id'])
                head.keycloak = django_keycloak_group
                head.save()
        print(f'{group}')
        if group:
            keycloak_admin.add_group_permissions(group)
        else:
            raise Exception('No group created or found')

        for child in head.children:
            self.recursive_group_initialisation(child, group['id'])

    def get_keycloak_group(self, keycloak_id, head):
        try:
            group = keycloak_admin.get_group(group_id=keycloak_id)
        except KeycloakGetError:
            pass
        else:
            if group and group['name'] == head.name:
                return group, True
        return None, False
