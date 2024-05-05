from django.urls import include, path
from rest_framework_nested import routers

from . import views

router = routers.SimpleRouter()
router.register(r'issue-read', views.IssueReadViewSet, basename='issue-read')
router.register(r'issue', views.IssueViewSet, basename='issue')
router.register(r'issue-init-create', views.IssueInitCreateViewSet, basename='issue-init-create')


router.register(r'issue-type-read', views.IssueTypeReadViewSet, basename='issue-type-read')
router.register(r'issue-type-read-short', views.IssueTypeReadShortViewSet, basename='issue-type-read-short')
router.register(r'issue-type', views.IssueTypeViewSet, basename='issue-type')

router.register(r'message-read', views.MessageReadViewSet, basename='message-read')
router.register(r'message', views.MessageViewSet, basename='message')

router.register(r'message-prio', views.MessagePriorityChoiceViewSet, basename='message-prio')
router.register(r'message-statuses', views.MessageStatusChoiceViewSet, basename='message-statuses')



urlpatterns = [
    path('', include(router.urls)),
]
