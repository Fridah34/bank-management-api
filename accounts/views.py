# accounts/views.py
from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from .models import Account
from .serializers import AccountSerializer, AccountCreateSerializer

class IsOwnerOrAdmin(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        user = request.user
        # Safe guard: user might be AnonymousUser
        if not user or not user.is_authenticated:
            return False
        # Allow admins or owners
        return getattr(user, "role", "") == "admin" or obj.user == user

class AccountViewSet(viewsets.ModelViewSet):
    """
    Admins can list all accounts.
    Owners can retrieve their accounts, create new accounts, and view/update their own accounts.
    """
    queryset = Account.objects.all().select_related("user")
    serializer_class = AccountSerializer

    def get_permissions(self):
        if self.action == "list":
            return [permissions.IsAuthenticated(), permissions.IsAdminUser()]
        if self.action in ["create"]:
            return [permissions.IsAuthenticated()]
        if self.action in ["retrieve", "update", "partial_update", "destroy"]:
            return [permissions.IsAuthenticated(), IsOwnerOrAdmin()]
        return [permissions.IsAuthenticated()]

    def get_serializer_class(self):
        if self.action == "create":
            return AccountCreateSerializer
        return AccountSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
