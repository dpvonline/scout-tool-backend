from django.urls import include, path
from rest_framework_nested import routers

from . import views

router = routers.SimpleRouter()
router.register(r'group', views.AllGroupsViewSet, basename='group')
router.register(r'group-search', views.GroupSearchViewSet, basename='group-search')

group_router = routers.NestedSimpleRouter(router, r'group', lookup='group')
group_router.register(r'members', views.GroupMembersViewSet, basename='members')
group_router.register(r'requests', views.RequestGroupAccessViewSet, basename='requests')
group_router.register(r'parents', views.GroupParentViewSet, basename='parents')


urlpatterns = [
    path('', include(router.urls)),
    path('', include(group_router.urls)),
]
