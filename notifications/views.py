from django.core.cache import cache
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from drf_yasg.utils import swagger_auto_schema
from .models import Notification
from .serializers import NotificationSerializer
from logger.logging import logger

CACHE_TTL = getattr(settings, 'CACHE_TTL', 300)


class NotificationListView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="Get a list of notifications",
        responses={200: NotificationSerializer(many=True)}
    )
    def get(self, request):
        try:
            cache_key = f'notifications_{request.user.id}'
            cached_notifications = cache.get(cache_key)

            if cached_notifications:
                logger.info("Notifications fetched from cache")
                return Response(cached_notifications)

            notifications = Notification.objects.filter(user=request.user).order_by('-created_at')
            serializer = NotificationSerializer(notifications, many=True)
            cache.set(cache_key, serializer.data, timeout=CACHE_TTL)
            logger.info("Notifications fetched from database and cached")
            return Response(serializer.data)

        except Exception as e:
            logger.error(f"Error fetching notifications: {e}")
            return Response({"error": "An error occurred while fetching notifications"}, status=500)

    @swagger_auto_schema(
        operation_summary="Create a notification",
        request_body=NotificationSerializer,
        responses={201: NotificationSerializer}
    )
    def post(self, request):
        serializer = NotificationSerializer(data=request.data)
        if serializer.is_valid():
            notification = serializer.save(user=request.user)
            cache.delete(f'notifications_{request.user.id}')
            logger.info(f"Notification created for user {request.user.id}")
            return Response(serializer.data, status=201)

        return Response(serializer.errors, status=400)


class NotificationDetailView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="Update the notification",
        request_body=NotificationSerializer,
        responses={200: NotificationSerializer}
    )
    def put(self, request, pk):
        try:
            notification = Notification.objects.get(pk=pk, user=request.user)
            serializer = NotificationSerializer(notification, data=request.data, partial=True)

            if serializer.is_valid():
                serializer.save()
                cache.delete(f'notifications_{request.user.id}')
                return Response(serializer.data)

            return Response(serializer.errors, status=400)

        except Notification.DoesNotExist:
            return Response({"error": "Notification not found"}, status=404)

    @swagger_auto_schema(
        operation_summary="Delete a notification",
        responses={204: "The notification was successfully deleted"}
    )
    def delete(self, request, pk):
        try:
            notification = Notification.objects.get(pk=pk, user=request.user)
            notification.delete()
            cache.delete(f'notifications_{request.user.id}')
            return Response({"message": "Notification deleted successfully"}, status=204)

        except Notification.DoesNotExist:
            return Response({"error": "Notification not found"}, status=404)
