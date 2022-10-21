from django.core.management.base import BaseCommand
from keycloak import KeycloakAdmin, KeycloakGetError

from basic.choices import ScoutOrganisationLevelChoices
from basic.models import ScoutHierarchy
from backend.settings import env


class Command(BaseCommand):
    help = 'check keycloak groups'

    def __init__(self, stdout=None, stderr=None, no_color=False, force_color=False):
        super(Command, self).__init__(stdout, stderr, no_color, force_color)
        self.keycloak_admin = KeycloakAdmin(
            server_url=env('BASE_URI'),
            client_id=env('KEYCLOAK_ADMIN_USER'),
            client_secret_key=env('KEYCLOAK_ADMIN_PASSWORD'),
            realm_name=env('KEYCLOAK_APP_REALM'),
            user_realm_name=env('KEYCLOAK_APP_REALM'),
            verify=True
        )
        self.groups = {}

    def handle(self, *args, **options):
        all_groups = self.keycloak_admin.get_groups()

        for group in all_groups:
            self.groups[group['name']] = False
            self.get_subgroup(group)

        heads = ScoutHierarchy.objects.filter(parent=None)

        for head in heads:
            self.recursive_group_initialisation(head)

        print('')
        print('Missing Groups:')
        for key in self.groups:
            if not self.groups[key]:
                print(key)

    def get_subgroup(self, group):
        for sub_group in group['subGroups']:
            self.groups[sub_group['name']] = False
            if sub_group['subGroups']:
                self.get_subgroup(sub_group)

    def recursive_group_initialisation(self, head: ScoutHierarchy):
        initialized = False
        if head.keycloak_id:
            try:
                group = self.keycloak_admin.get_group(group_id=head.keycloak_id)
            except KeycloakGetError:
                pass
            else:
                if group and group['name'] == head.name:
                    initialized = True

        if not initialized:
            group = self.keycloak_admin.get_group_by_path(path=head.keycloak_group_name, search_in_subgroups=True)
            if group:
                initialized = True

        if not initialized:
            parent_id = None
            if head.parent:
                parent_normal_path = head.parent.keycloak_group_name
                parent_special_path = f'{head.parent.keycloak_group_name}/' \
                                      f'{ScoutOrganisationLevelChoices.get_level_choice_plural(head.level_choice)}'
                parent = self.keycloak_admin.get_group_by_path(path=parent_special_path, search_in_subgroups=True)

                if parent:
                    parent_id = parent['id']
                else:
                    parent_normal = self.keycloak_admin.get_group_by_path(
                        path=parent_normal_path,
                        search_in_subgroups=True
                    )
                    parent_normal_id = parent_normal['id']
                    payload = {'name': ScoutOrganisationLevelChoices.get_level_choice_plural(head.level_choice)}
                    parent_special = self.keycloak_admin.create_group(payload=payload, parent=parent_normal_id)
                    parent_id = parent_special

            payload = {'name': head.name}
            if parent_id:
                child_group = self.keycloak_admin.create_group(payload=payload, parent=parent_id)
            else:
                child_group = self.keycloak_admin.create_group(payload=payload)

            print(f'created group: {child_group=}')

            if head.keycloak_id is None or head.keycloak_id != child_group:
                head.keycloak_id = child_group
                head.save()

        self.groups[head.name] = True

        for child in head.children:
            self.recursive_group_initialisation(child)
