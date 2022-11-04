from django.contrib.auth import get_user_model
from rest_framework import viewsets, status, mixins
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from authentication.models import CustomUser
from authentication.serializers import UserSerializer
from backend.settings import keycloak_admin
from keycloak_auth.api_exceptions import NoGroupId
from keycloak_auth.helper import check_group_id
from keycloak_auth.serializers import UserListSerializer

User: CustomUser = get_user_model()


class AllGroupsViewSet(viewsets.ViewSet):
    # permission_classes = [IsAuthenticated]

    def list(self, request) -> Response:
        all_groups = keycloak_admin.get_groups()

        return Response(all_groups, status=status.HTTP_200_OK)

    def retrieve(self, request, *args, **kwargs) -> Response:
        group_id = kwargs.get("pk", None)
        if not group_id or not check_group_id(group_id):
            raise NoGroupId()

        group = keycloak_admin.get_group(group_id=group_id)
        return Response(group, status=status.HTTP_200_OK)


class GroupMembersViewSet(mixins.RetrieveModelMixin, mixins.ListModelMixin, GenericViewSet):
    # permission_classes = [IsAuthenticated]
    serializer_class = UserListSerializer

    def get_queryset(self):
        group_id = self.kwargs.get("group_pk", None)
        if not group_id:
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
