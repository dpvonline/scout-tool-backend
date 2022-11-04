from django.core.management.base import BaseCommand
from keycloak import KeycloakGetError

from backend.settings import keycloak_admin
from basic.choices import ScoutOrganisationLevelChoices
from basic.models import ScoutHierarchy

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

        for group in all_groups:
            self.get_subgroup(group)

        heads = ScoutHierarchy.objects.filter(parent=None)

        for head in heads:
            self.recursive_group_initialisation(head)

        if self.groups_added:
            print('')
            print('added groups:')
            for group in self.groups_added:
                print(group)

        print('Checks completed')

    def get_subgroup(self, group):
        for sub_group in group['subGroups']:
            if sub_group['subGroups']:
                self.get_subgroup(sub_group)

    def recursive_group_initialisation(self, head: ScoutHierarchy):
        initialized = False
        group = None
        if head.keycloak_id:
            try:
                group = keycloak_admin.get_group(group_id=head.keycloak.keycloak_id)
            except KeycloakGetError:
                pass
            else:
                if group and group['name'] == head.name:
                    initialized = True

        if not initialized:
            group = keycloak_admin.get_group_by_path(path=head.keycloak_group_name, search_in_subgroups=True)
            if group:
                initialized = True

        if not initialized:
            parent_id = None
            if head.parent:
                parent_normal_path = head.parent.keycloak_group_name
                parent_special_path = f'{head.parent.keycloak_group_name}/' \
                                      f'{ScoutOrganisationLevelChoices.get_level_choice_plural(head.level_choice)}'
                parent = keycloak_admin.get_group_by_path(path=parent_special_path, search_in_subgroups=True)

                if parent:
                    parent_id = parent['id']
                else:
                    parent_normal = keycloak_admin.get_group_by_path(
                        path=parent_normal_path,
                        search_in_subgroups=True
                    )
                    parent_normal_id = parent_normal['id']
                    payload = {'name': ScoutOrganisationLevelChoices.get_level_choice_plural(head.level_choice)}
                    parent_special = keycloak_admin.create_group(payload=payload, parent=parent_normal_id)
                    parent_id = parent_special

            payload = {'name': head.name}
            if parent_id:
                child_group = keycloak_admin.create_group(payload=payload, parent=parent_id)
            else:
                child_group = keycloak_admin.create_group(payload=payload)

            group = keycloak_admin.get_group(group_id=child_group)

            self.groups_added.append(head.name)

            # if head.keycloak is None or head.keycloak.keycloak_id != child_group:
            #     keycloak_group, _ = get_or_create_keycloak_group(group, parent_id)
            #     head.keycloak = keycloak_group
            #     head.save()

        if group:
            keycloak_admin.add_group_permissions(group)
        else:
            raise Exception('No group created or found')

        for child in head.children:
            self.recursive_group_initialisation(child)
