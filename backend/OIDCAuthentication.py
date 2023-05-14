from __future__ import annotations

from datetime import datetime, timedelta, timezone

from django.contrib.auth.models import Group
from django.db import transaction, IntegrityError
from django.db.models import Q
from mozilla_django_oidc.auth import OIDCAuthenticationBackend

from authentication.models import Person, CustomUser
from basic.models import ScoutHierarchy


class MyOIDCAB(OIDCAuthenticationBackend):
    def get_username(self, claims: dict) -> str:
        return claims.get('preferred_username')

    def create_user(self, claims: dict) -> CustomUser | None:
        try:
            user: CustomUser = super(MyOIDCAB, self).create_user(claims)
            user.person = Person.objects.create()
            user.keycloak_id = claims['sub']
            user.save()

            self.set_user_info(user, claims)
            self.update_groups(user, claims)

            return user
        except IntegrityError:
            pass

        return None

    def update_user(self, user: CustomUser, claims: dict) -> CustomUser:
        self.set_user_info(user, claims)
        self.update_groups(user, claims)
        return user

    def filter_users_by_claims(self, claims: dict) -> CustomUser:
        """Return all users matching the specified email."""
        preferred_username = claims.get('preferred_username')
        if not preferred_username:
            return self.UserModel.objects.none()
        return self.UserModel.objects.filter(username__iexact=preferred_username)

    def verify_claims(self, claims):
        """Verify the provided claims to decide if authentication should be allowed."""

        # Verify claims required by default configuration
        email_verified = 'email' in claims
        username_verified = 'preferred_username' in claims

        return email_verified and username_verified

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

    def set_user_info(self, user: CustomUser, claims: dict):
        edited = False

        if not user.keycloak_id and user.keycloak_id != claims['sub']:
            user.keycloak_id = claims['sub']
            edited = True

        if not user.person:
            user.person = Person.objects.create()
            edited = True

        if claims.get('fahrtenname', ''):
            if user.person.scout_name != claims.get('fahrtenname', ''):
                user.person.scout_name = claims.get('fahrtenname', '')
                edited = True
        else:
            if user.person.scout_name != claims.get('given_name', ''):
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

        if stamm and bund and not user.person.scout_group:
            stamm = stamm.replace('stamm', '')
            found_bund = ScoutHierarchy.objects.filter(level=3, abbreviation=bund).first()
            found_stamm = ScoutHierarchy.objects \
                .filter(Q(name__contains=stamm, parent=found_bund) | Q(name__contains=stamm, parent__parent=found_bund))
            if len(found_stamm) == 1:
                user.person.scout_group = found_stamm.first()
                edited = True

        if edited:
            user.save()
            user.person.save()
