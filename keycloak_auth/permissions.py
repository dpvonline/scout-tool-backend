from django.contrib.auth import get_user_model
from rest_framework import permissions
from rest_framework.permissions import SAFE_METHODS
from rest_framework.request import Request

User = get_user_model()


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

        if role_name not in request.user.groups:
            return False

        return True


class CanQueryGroups(permissions.BasePermission):
    message = 'Keine Berechtigung um Gruppen einzusehen'

    def has_permission(self, request: Request, view) -> bool:
        role_name = 'query-groups'

        if role_name not in request.user.groups:
            return False

        return True


class CanManageGroup(permissions.BasePermission):
    message = 'Keine Berechtigung um Gruppen einzusehen'

    def has_permission(self, request: Request, view) -> bool:
        group_id = request.data.get('groupId')
        role_name = "group-" + group_id + "-admin-role"

        if role_name not in request.user.groups:
            return False

        return True


class CanManageParentGroup(permissions.BasePermission):
    message = 'Keine Berechtigung um Gruppen einzusehen'

    def has_permission(self, request: Request, view) -> bool:
        group_id = request.data.get('parentGroupId')
        role_name = "group-" + group_id + "-admin-role"

        if role_name not in request.user.groups:
            return False

        return True
