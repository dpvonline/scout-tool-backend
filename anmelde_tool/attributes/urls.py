from django.urls import include, path
from rest_framework_nested import routers

from . import views

router = routers.SimpleRouter()
router.register(r'attributes', views.AttributeViewSet)
router.register(r'attribute-choices', views.AttributeTypeViewSet, basename='attribute-choices')
router.register(r'travel-type-choices', views.TravelTypeViewSet, basename='travel-type-choices')


urlpatterns = [
    path('', include(router.urls)),
]
