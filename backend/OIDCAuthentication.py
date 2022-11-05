from authentication.models import Person, CustomUser
from basic.models import ScoutHierarchy
from django.contrib.auth.models import Group
from django.db import transaction
from django.db.models import Q
from mozilla_django_oidc.auth import OIDCAuthenticationBackend


class MyOIDCAB(OIDCAuthenticationBackend):

    def create_user(self, claims):
        user: CustomUser = super(MyOIDCAB, self).create_user(claims)
        person = Person.objects.create()
        user.person = person
        user.save()

        self.set_user_info(user, claims)
        self.update_groups(user, claims)

        return user

    def update_user(self, user, claims):
        self.set_user_info(user, claims)
        self.update_groups(user, claims)
        return user

    def update_groups(self, user, claims):
        """
        Transform roles obtained from keycloak into Django Groups and
        add them to the user. Note that any role not passed via keycloak
        will be removed from the user.
        """

        with transaction.atomic():
            user.groups.clear()
            for role in claims.get('roles', []):
                group, _ = Group.objects.get_or_create(name=role)
                group.user_set.add(user)

    def set_user_info(self, user, claims):
        edited = False
        print(claims)
        if user.username != claims.get('preferred_username', ''):
            user.username = claims.get('preferred_username', '')
            edited = True

        if claims.get('fahrtenname', ''):
            if user.scout_name is not claims.get('fahrtenname', ''):
                user.scout_name = claims.get('fahrtenname', '')
                user.person.scout_name = claims.get('fahrtenname', '')
                edited = True
        else:
            if user.scout_name != claims.get('given_name', ''):
                user.scout_name = claims.get('given_name', '')
                user.person.scout_name = claims.get('given_name', '')
                edited = True

        if user.email != claims.get('email', ''):
            user.email = claims.get('email', '')
            user.person.email = claims.get('email', '')
            edited = True

        if user.first_name != claims.get('given_name', ''):
            user.first_name = claims.get('given_name', '')
            user.person.first_name = claims.get('given_name', '')
            edited = True

        if user.last_name != claims.get('family_name', ''):
            user.last_name = claims.get('family_name', '')
            user.person.last_name = claims.get('family_name', '')
            edited = True

        if 'anmelde_tool_team' in claims.get('roles', []):
            if not user.is_staff:
                edited = True
                user.is_staff = True
        elif user.is_staff:
            edited = True
            user.is_staff = False

        stamm = claims.get('stamm', '')
        bund = claims.get('bund', '')

        if stamm and bund and not user.scout_organisation:
            stamm = stamm.replace('stamm', '')
            found_bund = ScoutHierarchy.objects.filter(level=3, abbreviation=bund).first()
            found_stamm = ScoutHierarchy.objects \
                .filter(Q(name__contains=stamm, parent=found_bund) | Q(name__contains=stamm, parent__parent=found_bund))
            if len(found_stamm) == 1:
                user.scout_organisation = found_stamm.first()
                user.person.scout_group = found_stamm.first()
                edited = True

        if edited:
            user.save()
            user.person.save()
