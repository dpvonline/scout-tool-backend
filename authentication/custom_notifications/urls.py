from django.urls import include, path
from rest_framework_nested import routers

from . import views

router = routers.SimpleRouter()
router.register('all', views.AllNotificationViewSet, basename='all')
router.register('unread', views.UnreadNotificationViewSet, basename='unread')
router.register('read', views.ReadNotificationViewSet, basename='read')
router.register('mark-as-read', views.MarkAsReadViewSet, basename='mark-as-read')
router.register('mark-as-unread', views.MarkAsUnreadViewSet, basename='mark-as-unread')
router.register('delete', views.DeleteViewSet, basename='delete')
router.register('count', views.NotificationCountViewSet, basename='unread-count')

urlpatterns = [
    path('', include(router.urls)),
]
