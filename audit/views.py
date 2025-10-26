from django.shortcuts import render
from rest_framework import viewsets, permissions
from .models import AuditLog
from .serializers import AuditLogSerializer


class AuditLogViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for viewing audit logs.
    Only authenticated users can access.
    Superusers and staff can view all logs.
    Regular users can only view their own logs.
    """
    serializer_class = AuditLogSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_staff or user.is_superuser:
            return AuditLog.objects.all()
        return AuditLog.objects.filter(user=user).order_by("-created_at")


