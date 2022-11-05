from django.contrib.auth import get_user_model
from keycloak import KeycloakGetError
from rest_framework import viewsets, status, mixins
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from authentication.models import CustomUser, RequestGroupAccess
from authentication.serializers import UserSerializer, RequestGroupAccessSerializer
from backend.settings import keycloak_admin
from keycloak_auth.api_exceptions import NoGroupId, AlreadyInGroup, AlreadyAccessRequested, WrongParentGroupId
from keycloak_auth.helper import check_group_id
from keycloak_auth.models import KeycloakGroup
from keycloak_auth.serializers import UserListSerializer, CreateGroupSerializer, UpdateGroupSerializer, \
    GroupSearchSerializer

User: CustomUser = get_user_model()


def get_group_id(kwargs):
    group_id = kwargs.get("group_pk", None)
    if not group_id or not check_group_id(group_id):
        group_id = kwargs.get("pk", None)
    if not group_id or not check_group_id(group_id):
        raise NoGroupId()
    return group_id


class AllGroupsViewSet(viewsets.ViewSet):
    # permission_classes = [IsAuthenticated]

    def create(self, request) -> Response:
        serializer = CreateGroupSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        parent_id = serializer.data.get('parent_id')
        parent_group = None
        if parent_id:
            try:
                parent_group = keycloak_admin.get_group(group_id=parent_id)
            except KeycloakGetError:
                raise WrongParentGroupId()

        payload = {'name': serializer.data['name']}
        if parent_group:
            new_group_id = keycloak_admin.create_group(payload=payload, parent=parent_id)
        else:
            new_group_id = keycloak_admin.create_group(payload=payload)

        new_group = keycloak_admin.get_group(new_group_id)
        return Response(new_group, status=status.HTTP_200_OK)

    def update(self, request, *args, **kwargs):
        group_id = get_group_id(kwargs)
        serializer = UpdateGroupSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        keycloak_admin.get_group(group_id=group_id)

        payload = {}
        if serializer.data.get('name'):
            payload = {'name': serializer.data['name']}

        if serializer.data.get('parent_id'):
            keycloak_admin.move_group(payload=payload, parent=serializer.data['parent_id'])

        new_group = keycloak_admin.get_group(group_id=group_id)
        return Response(new_group, status=status.HTTP_200_OK)

    def delete(self, request, *args, **kwargs):
        group_id = get_group_id(kwargs)
        keycloak_admin.delete_group(group_id=group_id)
        return Response(status.HTTP_204_NO_CONTENT)

    def list(self, request) -> Response:
        all_groups = keycloak_admin.get_groups()

        return Response(all_groups, status=status.HTTP_200_OK)

    def retrieve(self, request, *args, **kwargs) -> Response:
        group_id = get_group_id(kwargs)
        group = keycloak_admin.get_group(group_id=group_id)
        return Response(group, status=status.HTTP_200_OK)


class GroupSearchViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    def list(self, request):
        search_params = request.GET.get('search')
        results = KeycloakGroup.objects.filter(name__icontains=search_params)
        serializer = GroupSearchSerializer(results, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class GroupMembersViewSet(mixins.RetrieveModelMixin, mixins.ListModelMixin, GenericViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = UserListSerializer

    def get_queryset(self):
        group_id = self.kwargs.get("group_pk", None)
        if not group_id or not check_group_id(group_id):
            raise NoGroupId()
        group_members = keycloak_admin.get_group_members(group_id=group_id)
        ids = [val['id'] for val in group_members if val['enabled']]
        user = User.objects.filter(keycloak_id__in=ids)
        return user

    def get_serializer_class(self):
        serializer = {
            # 'create': registration_serializers.RegistrationParticipantSerializer,
            'retrieve': UserSerializer,
            'list': UserListSerializer,
            # 'update': registration_serializers.RegistrationParticipantSerializer,
            # 'destroy': registration_serializers.RegistrationParticipantSerializer
        }
        return serializer.get(self.action, UserListSerializer)


class RequestGroupAccessViewSet(viewsets.ModelViewSet):
    serializer_class = RequestGroupAccessSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs) -> Response:
        group_id = get_group_id(self.kwargs)
        user_groups = keycloak_admin.get_user_groups(request.user.keycloak_id)
        keycloak_group = get_object_or_404(KeycloakGroup, keycloak_id=group_id)

        if any(val['id'] == keycloak_group.keycloak_id for val in user_groups):
            raise AlreadyInGroup()

        if RequestGroupAccess.objects.filter(user=request.user, group=keycloak_group).exists():
            raise AlreadyAccessRequested()

        request.data['group'] = keycloak_group.id
        request.data['accepted'] = False
        request.data['declined'] = False
        if not request.data.get('user'):
            request.data['user'] = request.user.id

        return super().create(request, *args, **kwargs)

    def get_queryset(self):
        group_id = get_group_id(self.kwargs)
        requests = RequestGroupAccess.objects.filter(group__keycloak_id=group_id)
        return requests


class GroupParentViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    def list(self, request, *args, **kwargs):
        group_id = get_group_id(kwargs)
        results = KeycloakGroup.objects.filter(keycloak_id=group_id).first()
        serializer = GroupSearchSerializer(results, many=False)
        return Response(serializer.data, status=status.HTTP_200_OK)
