from django.urls import include, path
from rest_framework_nested import routers
from . import views

router = routers.SimpleRouter()
router.register(r'event-type-group', views.RegistrationTypeGroupViewSet, basename='event-type-group')
router.register(r'event-type-single', views.RegistrationTypeSingleViewSet, basename='event-type-single')
router.register(r'leader-types', views.LeaderTypesViewSet, basename='leader-types')
router.register(r'scout-level-types', views.ScoutLevelTypesViewSet, basename='scout-level-types')
router.register(r'file-type', views.FileTypeViewSet, basename='file-type')
router.register(r'file-generation-status', views.FileGenerationStatusViewSet, basename='file-generation-status')
router.register(r'file-extension', views.FileExtensionViewSet, basename='file-extension')
router.register(r'workshop-type', views.WorkshopTypeViewSet, basename='workshop-type')

# Wire up our API using automatic URL routing.
# Additionally, we include login URLs for the browsable API.
urlpatterns = [
    path('', include(router.urls)),
]
