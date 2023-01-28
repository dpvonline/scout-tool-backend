from django.urls import include, path
from rest_framework_nested import routers

from . import views

router = routers.SimpleRouter()
router.register(r'register', views.RegisterViewSet, basename="register")
router.register(r'personal-data', views.PersonalData, basename='personal-data')

router.register(r'my-requests', views.MyDecidableRequestGroupAccessViewSet, basename='my-requests')
router.register(r'my-own-requests', views.MyOwnRequestGroupAccessViewSet, basename='my-requests')

router.register(r'my-groups', views.UserGroupViewSet, basename='my-groups')
router.register(r'my-permissions', views.UserPermissionViewSet, basename='my-permissions')

router.register(r'check-username', views.CheckUsername, basename='check-username')
router.register(r'check-email', views.CheckEmail, basename='check-email')
router.register(r'check-password', views.CheckPassword, basename='check-password')

router.register(r'responsible', views.ResponsiblePersonViewSet, basename='responsible')
router.register(r'groups', views.GroupViewSet, basename='groups')

router.register(r'email-settings', views.EmailSettingsViewSet, basename='email-settings')
router.register(r'email-notification-types', views.EmailNotificationTypeViewSet, basename='email-notification-types')
router.register(r'bundespost-types', views.BundesPostViewSet, basename='bundespost-types')

# Wire up our API using automatic URL routing.
# Additionally, we include login URLs for the browsable API.
urlpatterns = [
    path('', include(router.urls)),
]
