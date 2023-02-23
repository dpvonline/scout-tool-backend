from django.urls import include, path
from rest_framework_nested import routers

from . import views

router = routers.SimpleRouter()
router.register(r'issue-read', views.IssueReadViewSet)
router.register(r'issue', views.IssueViewSet)
router.register(r'issue-init-create', views.IssueInitCreateViewSet)


router.register(r'issue-type-read', views.IssueTypeReadViewSet)
router.register(r'issue-type-read-short', views.IssueTypeReadShortViewSet)
router.register(r'issue-type', views.IssueTypeViewSet)

router.register(r'message-read', views.MessageReadViewSet)
router.register(r'message', views.MessageViewSet)

router.register(r'message-prio', views.MessagePriorityChoiseViewSet, basename='message-prio')
router.register(r'message-statuses', views.MessageStatusChoiseViewSet, basename='message-statuses')



urlpatterns = [
    path('', include(router.urls)),
]