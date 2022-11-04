from django.contrib.auth import get_user_model
from rest_framework import permissions
from rest_framework.permissions import SAFE_METHODS
from rest_framework.request import Request
from .enums import PermissionType

User = get_user_model()


def request_access(request, role_name: str) -> bool:
    if role_name not in request.user.groups:
        return False

    return True


def request_group_access(request, group_id: str, permission_type: PermissionType) -> bool:
    role_name = f'group-{group_id}-{permission_type.value}-role'
    return request_access(request, role_name)


class IsStaffOrReadOnly(permissions.BasePermission):
    message = 'Kann nur von den Admins bearbeitet werden'

    def has_permission(self, request: Request, view) -> bool:
        return bool(
            request.method in SAFE_METHODS or
            (request.user and request.user.is_authenticated and request.user.is_staff)
        )


class CanViewClients(permissions.BasePermission):
    message = 'Keine Berechtigung um Clients einzusehen'

    def has_permission(self, request: Request, view) -> bool:
        role_name = 'view-clients'
        return request_access(request, role_name)


class CanQueryGroups(permissions.BasePermission):
    message = 'Keine Berechtigung um Gruppen einzusehen'

    def has_permission(self, request: Request, view) -> bool:
        role_name = 'query-groups'
        return request_group_access(request, role_name)


class CanManageGroup(permissions.BasePermission):
    message = 'Keine Berechtigung um Gruppen bearbeiten'

    def has_permission(self, request: Request, view) -> bool:
        group_id = request.data.get('groupId')
        return request_group_access(request, group_id, PermissionType.ADMIN)


class CanManageParentGroup(permissions.BasePermission):
    message = 'Keine Berechtigung um Gruppen zu bearbeiten'

    def has_permission(self, request: Request, view) -> bool:
        group_id = request.data.get('parentGroupId')
        return request_group_access(request, group_id, PermissionType.ADMIN)


class CanViewGroup(permissions.BasePermission):
    message = 'Keine Berechtigung um Gruppen zu einzusehen'

    def has_permission(self, request: Request, view) -> bool:
        group_id = request.data.get('groupId')
        return request_group_access(request, group_id, PermissionType.VIEW)
