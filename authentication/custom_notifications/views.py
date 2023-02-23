from notifications.models import Notification
from rest_framework import viewsets, status, mixins
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from authentication.custom_notifications.serializers import NotificationSerializer, UpdateNotificationSerializer


def get_queryset(request):
    serializer = UpdateNotificationSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    queryset = Notification.objects.filter(recipient_id=request.user.id)

    ids = serializer.data.get('ids', None)
    if ids:
        queryset = queryset.filter(id__in=ids)

    return queryset


class AllNotificationViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = NotificationSerializer

    def get_queryset(self):
        return Notification.objects.filter(recipient_id=self.request.user.id)


class UnreadNotificationViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = NotificationSerializer

    def get_queryset(self):
        return Notification.objects.filter(recipient_id=self.request.user.id, unread=True)


class ReadNotificationViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = NotificationSerializer

    def get_queryset(self):
        return Notification.objects.filter(recipient_id=self.request.user.id, unread=False)


class MarkAsReadViewSet(mixins.CreateModelMixin, GenericViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = UpdateNotificationSerializer

    def create(self, request, *args, **kwargs):
        queryset = get_queryset(request)

        queryset.update(unread=False)
        return Response({'code': 'OK'}, status=status.HTTP_200_OK)


class MarkAsUnreadViewSet(mixins.CreateModelMixin, GenericViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = NotificationSerializer

    def create(self, request, *args, **kwargs):
        queryset = get_queryset(request)

        queryset.update(unread=True)
        return Response({'code': 'OK'}, status=status.HTTP_200_OK)


class DeleteViewSet(mixins.CreateModelMixin, GenericViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = NotificationSerializer

    def create(self, request, *args, **kwargs):
        queryset = get_queryset(request)

        queryset.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class NotificationCountViewSet(mixins.ListModelMixin, GenericViewSet):
    permission_classes = [IsAuthenticated]

    def list(self, request, *args, **kwargs):
        queryset = Notification.objects.filter(recipient_id=request.user.id)
        all_count = queryset.count()
        unread_count = queryset.filter(unread=True).count()
        read_count = queryset.filter(unread=False).count()

        data = {
            'all': all_count,
            'unreadCount': unread_count,
            'readCount': read_count
        }
        return Response(data)
