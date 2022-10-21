from django.urls import include, path
from rest_framework_nested import routers

from . import views

router = routers.SimpleRouter()
router.register(r'message', views.MessageViewSet)
router.register(r'message-type', views.MessageTypeViewSet)


urlpatterns = [
    path('', include(router.urls)),
]