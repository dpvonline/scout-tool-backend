from django.db.models import Q
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status, viewsets

from backend.settings import keycloak_user
from messaging.models import Message, IssueType, Issue
from messaging.serializers import MessageSerializer, IssueReadSerializer, IssueTypeSerializer, IssueTypeReadSerializer, \
    IssueTypeReadShortSerializer, MessageReadSerializer, IssueSerializer
from basic.helper.choice_to_json import choice_to_json
from .choices import MessagePriorityChoise, MessageStatusChoise
from authentication.models import CustomUser


# Issue
class IssueReadViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = IssueReadSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter]

    def get_queryset(self):
        if self.request.user.is_staff:
            return Issue.objects.all().order_by('-created_at')
        else:
            try:
                token = self.request.META.get('HTTP_AUTHORIZATION')
                keycloak_groups = keycloak_user.get_user_groups(token, self.request.user.keycloak_id)
                ids = [val['id'] for val in keycloak_groups]
                return Issue.objects.filter(
                    Q(created_by=self.request.user)
                    | Q(issue_type__responsable_groups__keycloak_id__in=ids)
                ).order_by('-created_at')
            except Exception as e:
                print(e)

        return Issue.objects.filter(created_by=self.request.user)


class IssueViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = IssueSerializer

    def get_queryset(self):
        if self.request.user.is_staff:
            return Issue.objects.all().order_by('-created_at')
        else:
            return Issue.objects.filter(created_by=self.request.user).order_by('-created_at')


class IssueInitCreateViewSet(viewsets.ModelViewSet):
    queryset = Issue.objects.all()
    serializer_class = IssueReadSerializer

    def create(self, request, *args, **kwargs):
        if request.user.id:
            request.data['created_by'] = CustomUser.objects.filter(id=request.user.id).first()
            request.data['created_by_name'] = None
            request.data['created_by_email'] = None
        else:
            request.data['created_by'] = None

        issue = Issue(
            created_by_name=request.data.get('created_by_name'),
            created_by_email=request.data.get('created_by_email'),
            created_by=request.data.get('created_by'),
            priority=request.data.get('priority'),
            issue_type_id=request.data.get('issue_type'),
            issue_subject=request.data.get('issue_subject'),
        )

        issue.save()

        message = Message(
            issue_id=issue.id,
            message_body=request.data.get('message_body'),
            created_by=request.data.get('created_by'),
        )
        message.save()

        return Response({'created issue and message'}, status=status.HTTP_201_CREATED)


# Message

class MessageReadViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = Message.objects.all().order_by('-created_at')
    serializer_class = MessageReadSerializer


class MessageViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = Message.objects.all().order_by('-created_at')
    serializer_class = MessageSerializer

    def create(self, request, *args, **kwargs) -> Response:
        request.data['created_by'] = request.user.id
        return super().create(request, *args, **kwargs)


# Issue-type

class IssueTypeReadViewSet(viewsets.ModelViewSet):
    queryset = IssueType.objects.all()
    serializer_class = IssueTypeReadSerializer


class IssueTypeViewSet(viewsets.ModelViewSet):
    queryset = IssueType.objects.all()
    serializer_class = IssueTypeSerializer


class IssueTypeReadShortViewSet(viewsets.ModelViewSet):
    queryset = IssueType.objects.all()
    serializer_class = IssueTypeReadShortSerializer


# Prio

class MessagePriorityChoiceViewSet(viewsets.ViewSet):
    """
    Viewset for message priorities
    """

    # pylint: disable=no-self-use
    def list(self, request) -> Response:
        """
        @param request: standard django request
        @return: Response which MessagePriorityChoise choices
        """
        result = choice_to_json(MessagePriorityChoise.choices)
        return Response(result, status=status.HTTP_200_OK)


# Status

class MessageStatusChoiceViewSet(viewsets.ViewSet):
    """
    Viewset for message statues
    """

    # pylint: disable=no-self-use
    def list(self, request) -> Response:
        """
        @param request: standard django request
        @return: Response which MessageStatusChoise choices
        """
        result = choice_to_json(MessageStatusChoise.choices)
        return Response(result, status=status.HTTP_200_OK)
