from django.urls import include, path
from rest_framework_nested import routers

from . import views

router = routers.SimpleRouter()
router.register(r'attribute-module', views.AttributeModuleViewSet)
router.register(r'attribute-choices', views.AttributeTypeViewSet, basename='attribute-choices')
router.register(r'travel-type-choices', views.TravelTypeViewSet, basename='travel-type-choices')

router.register(r'boolean-attribute', views.BooleanAttributeViewSet, basename='boolean-attribute')
router.register(r'string-attribute', views.StringAttributeViewSet, basename='string-attribute')
router.register(r'travel-attribute', views.TravelAttributeViewSet, basename='travel-attribute')
router.register(r'float-attribute', views.FloatAttributeViewSet, basename='float-attribute')
router.register(r'time-attribute', views.TimeAttributeViewSet, basename='time-attribute')
router.register(r'integer-attribute', views.IntegerAttributeViewSet, basename='integer-attribute')

urlpatterns = [
    path('', include(router.urls)),
]
