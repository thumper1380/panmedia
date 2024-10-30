# notification/views.py
from django.shortcuts import render

# Create your views here.
from rest_framework import viewsets, status
from .models import Notification
from .serializers import NotificationSerializer, NotificationWriteSerializer
from rest_framework.response import Response
from rest_framework.decorators import action
from django.shortcuts import get_object_or_404, redirect


class NotificationViewSet(viewsets.ViewSet):
    queryset = Notification.objects.all()
    serializer_class = NotificationSerializer
    permission_classes = []

    def get_serializer_class(self):
        if self.action in ['list', 'retrieve']:
            return NotificationSerializer
        return NotificationWriteSerializer

    def list(self, request):
        queryset = Notification.objects.filter(user=request.user)
        serializer = NotificationSerializer(queryset, many=True)
        return Response(serializer.data)
    
    def retrieve(self, request, pk=None):
        queryset = Notification.objects.filter(user=request.user)
        notification = get_object_or_404(queryset, pk=pk)
        serializer = NotificationSerializer(notification)
        return Response(serializer.data)

    # set as read 
    @action(methods=['PUT'], detail=True, url_path='read')
    def read(self, request, pk=None):
        notification = get_object_or_404(Notification, pk=pk)
        notification.is_read = True
        notification.save()
        return Response(status=status.HTTP_200_OK)
    
    @action(methods=['PUT'], detail=False, url_path='read-all')
    def read_all(self, request):
        notifications = Notification.objects.filter(user=request.user)
        for notification in notifications:
            notification.is_read = True
            notification.save()
        return Response(status=status.HTTP_200_OK)