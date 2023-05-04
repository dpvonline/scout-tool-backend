from django.urls import include, path
from rest_framework_nested import routers
from . import views

router = routers.SimpleRouter()
router.register(r'workshop', views.WorkshopViewSet, basename='workshop')

urlpatterns = [
    path('', include(router.urls)),
]
