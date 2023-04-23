from django.contrib.auth import get_user_model
from django.db.models import Q
from keycloak import KeycloakGetError, KeycloakAuthenticationError
from rest_framework import viewsets, status, mixins
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet
from rest_framework import filters
from notifications.signals import notify
from basic.helper import choice_to_json

from authentication.choices import RequestGroupAccessChoices
from authentication.models import CustomUser, RequestGroupAccess
from authentication.serializers import FullUserSerializer, RequestGroupAccessSerializer, \
    StatusRequestGroupAccessPutSerializer, StatusRequestGroupGetAccessSerializer
from backend.settings import keycloak_admin, keycloak_user
from keycloak_auth.api_exceptions import NoGroupId, AlreadyInGroup, AlreadyAccessRequested, WrongParentGroupId, \
    NotAuthorized, GroupAlreadyExists
from keycloak_auth.choices import CreateGroupChoices
from keycloak_auth.enums import PermissionType
from keycloak_auth.helper import check_group_id, get_or_create_keycloak_model
from keycloak_auth.models import KeycloakGroup
from keycloak_auth.permissions import request_group_access
from keycloak_auth.serializers import UserListSerializer, CreateGroupSerializer, UpdateGroupSerializer, \
    FullGroupSerializer, GroupParentSerializer, PartialUserSerializer, MemberUserIdSerializer, \
    SearchResultUserSerializer, GroupShortSerializer

User: CustomUser = get_user_model()


def get_group_id(kwargs):
    group_id = kwargs.get("group_pk", None)
    if not group_id or not check_group_id(group_id):
        group_id = kwargs.get("pk", None)
    if not group_id or not check_group_id(group_id):
        raise NoGroupId()
    return group_id


def search_user(request, users):
    search_param = request.GET.get('search')
    if search_param:
        users = users.filter(
            Q(username__icontains=search_param)
            | Q(email__icontains=search_param)
            | Q(person__first_name__icontains=search_param)
            | Q(person__last_name__icontains=search_param)
            | Q(person__email__icontains=search_param)
            | Q(person__last_name__icontains=search_param)
            | Q(person__scout_name__icontains=search_param)
            | Q(person__scout_group__name__icontains=search_param)
        )
    return users


class AllGroupsViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    def create(self, request) -> Response:
        serializer = CreateGroupSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        group_name = serializer.data.get('name')

        parent_id = serializer.data.get('parent_id')
        parent_group = None
        if parent_id:
            parent_group = KeycloakGroup.objects.filter(keycloak_id=parent_id)
            if not parent_group:
                raise WrongParentGroupId()
            else:
                parent_group = parent_group.first()

        if not request_group_access(request, parent_group.keycloak_id, PermissionType.ADMIN):
            raise NotAuthorized()

        group_exits = KeycloakGroup.objects.filter(name__iexact=group_name, parent__keycloak_id=parent_id).exists()
        if group_exits:
            raise GroupAlreadyExists()

        payload = {'name': group_name}

        group_id = keycloak_admin.create_group(payload=payload, parent=parent_id)

        group = keycloak_admin.get_group(group_id)
        view_role, admin_role = keycloak_admin.add_group_permissions(group, False)

        group_admin_name = {
            CreateGroupChoices.EVENT: 'Lagerleitung',
            CreateGroupChoices.AK: 'Ansprechperson',
            CreateGroupChoices.GRUPPE: 'Gruppenführung',
            CreateGroupChoices.OTHER: 'Admin'
        }

        group_type = serializer.data['type']
        admin_name = group_admin_name[group_type]
        admin_group_payload = {'name': admin_name}
        admin_group_id = keycloak_admin.create_group(payload=admin_group_payload, parent=group_id)
        admin_group = keycloak_admin.get_group(admin_group_id)

        admin_view_role, admin_admin_role = keycloak_admin.add_group_permissions(admin_group, True)

        keycloak_admin.assign_group_client_roles(
            admin_group_id,
            keycloak_admin.realm_management_client_id,
            [admin_role]
        )
        keycloak_admin.assign_group_client_roles(
            group_id,
            keycloak_admin.realm_management_client_id,
            [view_role, admin_view_role]
        )

        created_group, _ = get_or_create_keycloak_model(group, parent_group)
        created_admin_group, _ = get_or_create_keycloak_model(admin_group, created_group)

        user_id = request.user.keycloak_id
        keycloak_admin.group_user_add(user_id, admin_group_id)

        realm_role_payload = {'name': created_group.keycloak_role_name, 'description': group_name}
        realm_role_name = keycloak_admin.create_realm_role(realm_role_payload, skip_exists=True)
        realm_role = keycloak_admin.get_realm_role(realm_role_name)

        keycloak_admin.assign_group_realm_roles(group_id, [realm_role])
        keycloak_admin.add_realm_roles_to_client_scope(keycloak_admin.dpv_oidc_scope, realm_role)
        keycloak_admin.add_realm_roles_to_client_scope(keycloak_admin.dpv_saml_scope, realm_role)

        serializer = GroupParentSerializer(created_group, many=False, context={'request': request})
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        group_id = get_group_id(kwargs)
        serializer = UpdateGroupSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        group = get_object_or_404(KeycloakGroup, keycloak_id=group_id)
        edited = False
        new_name = serializer.data.get('name')
        new_parent = serializer.data.get('parent_id')
        if new_name and group.name != new_name:
            group.name = new_name
            edited = True
        if new_parent and group.parent.keycloak_id != new_parent:
            parent = get_object_or_404(KeycloakGroup, keycloak_id=new_parent)
            group.parent = parent
            edited: True
        if edited:
            group.save()

        serializer = GroupParentSerializer(group, many=False, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)

    def delete(self, request, *args, **kwargs):
        group_id = get_group_id(kwargs)
        group = get_object_or_404(KeycloakGroup, keycloak_id=group_id)
        group.delete()
        # keycloak_admin.delete_group(group_id=group_id)
        return Response(status.HTTP_204_NO_CONTENT)

    def list(self, request, *args, **kwargs) -> Response:
        search_params = request.GET.get('search')
        if search_params:
            results = KeycloakGroup.objects.filter(name__icontains=search_params)
        else:
            results = KeycloakGroup.objects.filter(parent=None)
        serializer = FullGroupSerializer(results, many=True, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)

    def retrieve(self, request, *args, **kwargs) -> Response:
        group_id = get_group_id(kwargs)
        group = get_object_or_404(KeycloakGroup, keycloak_id=group_id)
        serializer = FullGroupSerializer(group, many=False, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)


class ShortGroupsViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [IsAuthenticated]
    search_fields = ['name']
    filter_backends = (filters.SearchFilter,)
    queryset = KeycloakGroup.objects.all()
    serializer_class = GroupShortSerializer


class GroupMembersViewSet(mixins.RetrieveModelMixin, mixins.ListModelMixin, GenericViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = UserListSerializer

    def get_queryset(self):
        token = self.request.META.get('HTTP_AUTHORIZATION')
        group_id = get_group_id(self.kwargs)
        try:
            group_members = keycloak_user.get_group_users(token, group_id)
        except KeycloakGetError:
            raise NotAuthorized()
        ids = [val['id'] for val in group_members if val['enabled']]
        user = User.objects.filter(keycloak_id__in=ids)
        return user

    def get_serializer_class(self):
        serializer = {
            # 'create': registration_serializers.RegistrationParticipantSerializer,
            'retrieve': FullUserSerializer,
            'list': UserListSerializer,
            # 'update': registration_serializers.RegistrationParticipantSerializer,
            # 'destroy': registration_serializers.RegistrationParticipantSerializer
        }
        return serializer.get(self.action, UserListSerializer)


class RequestGroupAccessViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = StatusRequestGroupGetAccessSerializer

    def create(self, request, *args, **kwargs) -> Response:
        serializer = RequestGroupAccessSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        group_id = get_group_id(self.kwargs)
        token = self.request.META.get('HTTP_AUTHORIZATION')
        try:
            user_groups = keycloak_user.get_user_groups(token, request.user.keycloak_id)
        except KeycloakGetError:
            raise NotAuthorized()

        keycloak_group = get_object_or_404(KeycloakGroup, keycloak_id=group_id)

        if any(val['id'] == keycloak_group.keycloak_id for val in user_groups):
            raise AlreadyInGroup()
        if RequestGroupAccess.objects.filter(user=request.user, group=keycloak_group).exists():
            raise AlreadyAccessRequested()

        data = serializer.data
        data['group'] = keycloak_group.id
        if not data.get('user'):
            data['user'] = request.user.id

        serializer = StatusRequestGroupAccessPutSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)

        request_group = RequestGroupAccess.objects.get(id=serializer.data['id'])
        result_serializer = StatusRequestGroupGetAccessSerializer(request_group)
        return Response(result_serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def get_queryset(self):
        group_id = get_group_id(self.kwargs)
        requests = RequestGroupAccess.objects.filter(group__keycloak_id=group_id)
        return requests


def decide_request(requests_id: str, user: CustomUser, request_status: RequestGroupAccessChoices):
    group_access_request: RequestGroupAccess = get_object_or_404(RequestGroupAccess.objects.all(), id=requests_id)
    group_access_request.status = request_status
    group_access_request.checked_by = user
    group_access_request.save()
    serializer = StatusRequestGroupAccessPutSerializer(group_access_request, many=False)
    return Response(serializer.data, status=status.HTTP_200_OK)


class AcceptRequestGroupAccessViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs) -> Response:
        requests_id = kwargs.get("requests_pk", None)
        return decide_request(requests_id, request.user, RequestGroupAccessChoices.ACCEPTED)


class DeclineRequestGroupAccessViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs) -> Response:
        requests_id = kwargs.get("requests_pk", None)
        return decide_request(requests_id, request.user, RequestGroupAccessChoices.DECLINED)


class GroupParentViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    def list(self, request, *args, **kwargs):
        group_id = get_group_id(kwargs)
        results = KeycloakGroup.objects.filter(keycloak_id=group_id).first()
        serializer = FullGroupSerializer(results, many=False)
        return Response(serializer.data, status=status.HTTP_200_OK)


class AllMembersViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = PartialUserSerializer

    def get_queryset(self):
        token = self.request.META.get('HTTP_AUTHORIZATION')
        try:
            keycloak_user.get_all_users(token)
        except KeycloakGetError:
            raise NotAuthorized()
        except KeycloakAuthenticationError:
            raise NotAuthorized()

        # ids = [val['id'] for val in group_members if val['enabled']]

        users = User.objects.all()

        return search_user(self.request, users)


class InviteMemberViewSet(mixins.CreateModelMixin, GenericViewSet):
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        serializer = MemberUserIdSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user_id = serializer.data.get('user_id')
        group_id = get_group_id(kwargs)

        token = self.request.META.get('HTTP_AUTHORIZATION')
        # try:
        # keycloak_user.group_user_add(token, user_id, group_id)
        keycloak_admin.group_user_add(user_id, group_id)
        # except KeycloakGetError:
        #     raise NotAuthorized()

        user = User.objects.get(keycloak_id=user_id)
        group = KeycloakGroup.objects.get(keycloak_id=group_id)
        notify.send(
            sender=request.user,
            recipient=user,
            verb=f'Du wurdest einer Gruppe hinzugefügt.',
            target=group,
        )

        return Response('ok', status=status.HTTP_200_OK)


class LeaveGroupViewSet(mixins.CreateModelMixin, GenericViewSet):
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        user_id = request.user.keycloak_id
        group_id = get_group_id(kwargs)

        token = self.request.META.get('HTTP_AUTHORIZATION')
        # try:
        # keycloak_user.group_user_add(token, user_id, group_id)
        keycloak_admin.group_user_remove(user_id, group_id)
        # except KeycloakGetError:
        #     raise NotAuthorized()
        return Response('ok', status=status.HTTP_200_OK)


class KickMemberViewSet(mixins.CreateModelMixin, GenericViewSet):
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        serializer = MemberUserIdSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user_id = serializer.data.get('user_id')
        group_id = get_group_id(kwargs)

        token = self.request.META.get('HTTP_AUTHORIZATION')
        # try:
        # keycloak_user.group_user_add(token, user_id, group_id)
        keycloak_admin.group_user_remove(user_id, group_id)
        # except KeycloakGetError:
        #     raise NotAuthorized()

        user = User.objects.get(keycloak_id=user_id)
        group = KeycloakGroup.objects.get(keycloak_id=group_id)
        notify.send(
            sender=request.user,
            recipient=user,
            verb=f'Du wurdest aus einer Gruppe enfernt.',
            target=group,
        )
        return Response('ok', status=status.HTTP_200_OK)


class GroupGroupAdminViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = GroupParentSerializer

    def get_queryset(self):
        token = self.request.META.get('HTTP_AUTHORIZATION')
        group_id = get_group_id(self.kwargs)
        admin_name = f'group-{group_id}-admin-role'

        try:
            admin_groups = keycloak_admin.get_client_role_groups(keycloak_admin.realm_management_client_id, admin_name)
        except KeycloakGetError:
            raise NotAuthorized()
        except KeycloakAuthenticationError:
            raise NotAuthorized()

        ids = [val['id'] for val in admin_groups]
        queryset = KeycloakGroup.objects.filter(keycloak_id__in=ids)

        return queryset


class GroupUserAdminViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = SearchResultUserSerializer

    def get_queryset(self):
        token = self.request.META.get('HTTP_AUTHORIZATION')
        group_id = get_group_id(self.kwargs)
        admin_name = f'group-{group_id}-admin-role'

        try:
            admin_users = keycloak_admin.get_client_role_members(keycloak_admin.realm_management_client_id, admin_name)
        except KeycloakGetError:
            raise NotAuthorized()
        except KeycloakAuthenticationError:
            raise NotAuthorized()

        ids = [val['id'] for val in admin_users]
        queryset = User.objects.filter(keycloak_id__in=ids)

        return queryset


class GroupInvitableMemberViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = SearchResultUserSerializer

    def get_queryset(self):
        token = self.request.META.get('HTTP_AUTHORIZATION')
        group_id = get_group_id(self.kwargs)
        try:
            group_members = keycloak_user.get_group_users(token, group_id)
            keycloak_user.get_all_users(token)
        except KeycloakGetError:
            raise NotAuthorized()

        already_member_ids = [val['id'] for val in group_members if val['enabled']]
        # all_users_ids = [val['id'] for val in all_users if val['enabled']]

        users = User.objects.all().exclude(keycloak_id__in=already_member_ids)

        return search_user(self.request, users)


class GroupKickableMemberViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = SearchResultUserSerializer

    def get_queryset(self):
        token = self.request.META.get('HTTP_AUTHORIZATION')
        group_id = get_group_id(self.kwargs)
        try:
            group_members = keycloak_user.get_group_users(token, group_id)
        except KeycloakGetError:
            raise NotAuthorized()

        member_ids = [val['id'] for val in group_members if val['enabled']]

        users = User.objects.filter(keycloak_id__in=member_ids).exclude(keycloak_id__in=self.request.user.keycloak_id)

        return search_user(self.request, users)


class CreateGroupChoicesViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    def list(self, request) -> Response:
        result = choice_to_json(CreateGroupChoices.choices)
        return Response(result, status=status.HTTP_200_OK)
