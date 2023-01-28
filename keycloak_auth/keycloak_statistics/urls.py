from django.urls import include, path
from rest_framework_nested import routers

from . import views

router = routers.SimpleRouter()
router.register(r'group-count', views.GroupCountViewSet, basename='group-count')
router.register(r'user-count', views.UsersCountViewSet, basename='user-count')

# Wire up our API using automatic URL routing.
# Additionally, we include login URLs for the browsable API.
urlpatterns = [
    path('', include(router.urls)),
]
