from django.urls import include, path
from rest_framework_nested import routers

from . import views

router = routers.SimpleRouter()
router.register(r'group', views.AllGroupsViewSet, basename='group')
router.register(r'groups-short', views.ShortGroupsViewSet, basename='short-group')
router.register(r'members', views.AllMembersViewSet, basename='members')
router.register(r'create-group-choice', views.CreateGroupChoicesViewSet, basename='create-group-choice')

group_router = routers.NestedSimpleRouter(router, r'group', lookup='group')
group_router.register(r'members', views.GroupMembersViewSet, basename='members')
group_router.register(r'requests', views.RequestGroupAccessViewSet, basename='requests')
group_router.register(r'parents', views.GroupParentViewSet, basename='parents')
group_router.register(r'invite', views.InviteMemberViewSet, basename='invite')
group_router.register(r'leave', views.LeaveGroupViewSet, basename='leave')
group_router.register(r'kick', views.KickMemberViewSet, basename='kick')
group_router.register(r'group-admins', views.GroupGroupAdminViewSet, basename='group-admins')
group_router.register(r'user-admins', views.GroupUserAdminViewSet, basename='user-admins')
group_router.register(r'inevitable-members', views.GroupInvitableMemberViewSet, basename='inevitable-members')
group_router.register(r'kickable-members', views.GroupKickableMemberViewSet, basename='kickable-members')
group_router.register(r'create-group-choice', views.CreateGroupChoicesViewSet, basename='create-group-choice')

request_router = routers.NestedSimpleRouter(group_router, r'requests', lookup='requests')
request_router.register(r'accept', views.AcceptRequestGroupAccessViewSet, basename='accept')
request_router.register(r'decline', views.DeclineRequestGroupAccessViewSet, basename='decline')

urlpatterns = [
    path('', include(router.urls)),
    path('', include(group_router.urls)),
    path('', include(request_router.urls)),
    path('statistics/', include('keycloak_auth.keycloak_statistics.urls')),
]
