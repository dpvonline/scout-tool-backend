from django.db.models import QuerySet, Count

from rest_framework import mixins, viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from backend.settings import keycloak_admin


class UsersCountViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    permission_classes = [IsAuthenticated]

    def list(self, request, *args, **kwargs) -> Response:
        count = keycloak_admin.users_count()
        return Response({'count': count}, status=status.HTTP_200_OK)


class GroupCountViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    permission_classes = [IsAuthenticated]

    def list(self, request, *args, **kwargs) -> Response:
        count = keycloak_admin.groups_count()
        return Response(count, status=status.HTTP_200_OK)
