from django.contrib.auth import get_user_model
from keycloak import KeycloakGetError
from rest_framework import viewsets, status, mixins
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from authentication.choices import RequestGroupAccessChoices
from authentication.models import CustomUser, RequestGroupAccess
from authentication.serializers import FullUserSerializer, RequestGroupAccessSerializer, \
    StatusRequestGroupAccessPutSerializer, StatusRequestGroupGetAccessSerializer
from backend.settings import keycloak_admin, keycloak_user
from keycloak_auth.api_exceptions import NoGroupId, AlreadyInGroup, AlreadyAccessRequested, WrongParentGroupId, \
    NotAuthorized
from keycloak_auth.helper import check_group_id
from keycloak_auth.models import KeycloakGroup
from keycloak_auth.serializers import UserListSerializer, CreateGroupSerializer, UpdateGroupSerializer, \
    GroupSerializer, GroupParentSerializer

User: CustomUser = get_user_model()


def get_group_id(kwargs):
    group_id = kwargs.get("group_pk", None)
    if not group_id or not check_group_id(group_id):
        group_id = kwargs.get("pk", None)
    if not group_id or not check_group_id(group_id):
        raise NoGroupId()
    return group_id


class AllGroupsViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    def create(self, request) -> Response:
        serializer = CreateGroupSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        parent_id = serializer.data.get('parent_id')
        parent_group = None
        if parent_id:
            parent_group = KeycloakGroup.objects.filter(keycloak_id=parent_id)
            if not parent_group:
                raise WrongParentGroupId()

        created_group = KeycloakGroup.objects.create(
            name=serializer.data.get('name'),
            parent=parent_group
        )
        serializer = GroupParentSerializer(created_group, many=False, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)

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
        keycloak_admin.delete_group(group_id=group_id)
        return Response(status.HTTP_204_NO_CONTENT)

    def list(self, request, *args, **kwargs) -> Response:
        search_params = request.GET.get('search')
        if search_params:
            results = KeycloakGroup.objects.filter(name__icontains=search_params)
        else:
            results = KeycloakGroup.objects.filter(parent=None)
        serializer = GroupSerializer(results, many=True, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)

    def retrieve(self, request, *args, **kwargs) -> Response:
        group_id = get_group_id(kwargs)
        group = get_object_or_404(KeycloakGroup, keycloak_id=group_id)
        serializer = GroupSerializer(group, many=False, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)


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
    serializer_class = StatusRequestGroupAccessPutSerializer

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

        serializer = self.get_serializer(data=data)
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
        serializer = GroupSerializer(results, many=False)
        return Response(serializer.data, status=status.HTTP_200_OK)
