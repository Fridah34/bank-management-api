# accounts/views.py
from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from .models import Account
from rest_framework.decorators import action
from .serializers import AccountSerializer, AccountCreateSerializer
from decimal import Decimal, InvalidOperation

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
    
    @action(detail=True, methods=["post"], url_path="deposit")
    def deposit(self, request, pk=None):
        account = self.get_object()
        amount = request.data.get("amount")
        try:
            amount = Decimal(str(amount))
        except (InvalidOperation, TypeError, ValueError):
            return Response({"error": "Invalid amount."}, status=status.HTTP_400_BAD_REQUEST)

        if amount <= 0:
            return Response({"error": "Deposit amount must be positive."}, status=status.HTTP_400_BAD_REQUEST)

        account.balance += amount
        account.save()

        return Response({
            "message": "Deposit successful.",
            "new_balance": str(account.balance)
        }, status=status.HTTP_200_OK)

    @action(detail=True, methods=["post"], url_path="withdraw")
    def withdraw(self, request, pk=None):
        account = self.get_object()
        amount = request.data.get("amount")
        try:
            amount = Decimal(str(amount))
        except (InvalidOperation, TypeError, ValueError):
            return Response({"error": "Invalid amount."}, status=status.HTTP_400_BAD_REQUEST)

        if amount <= 0:
            return Response({"error": "Withdrawal amount must be positive."}, status=status.HTTP_400_BAD_REQUEST)
        if account.balance < amount:
            return Response({"error": "Insufficient funds."}, status=status.HTTP_400_BAD_REQUEST)

        account.balance -= amount
        account.save()

        return Response({
            "message": "Withdrawal successful.",
            "new_balance": account.balance
        }, status=status.HTTP_200_OK)
        
    @action(detail=True, methods=["post"], url_path="transfer")
    def transfer(self, request, pk=None):
        source_account = self.get_object()
        target_account_id = request.data.get("target_account_id")
        amount = request.data.get("amount")

        # Validate target account
        try:
            target_account = Account.objects.get(id=target_account_id)
        except Account.DoesNotExist:
            return Response({"error": "Target account not found."}, status=status.HTTP_404_NOT_FOUND)

        # Validate amount
        try:
            amount = Decimal(str(amount))
        except (InvalidOperation, TypeError, ValueError):
            return Response({"error": "Invalid amount."}, status=status.HTTP_400_BAD_REQUEST)

        if amount <= 0:
            return Response({"error": "Transfer amount must be positive."}, status=status.HTTP_400_BAD_REQUEST)

        if source_account.balance < amount:
            return Response({"error": "Insufficient funds."}, status=status.HTTP_400_BAD_REQUEST)

        # Perform transfer
        source_account.balance -= amount
        target_account.balance += amount
        source_account.save()
        target_account.save()

        return Response({
            "message": "Transfer successful.",
            "from_account": source_account.id,
            "to_account": target_account.id,
            "new_balance": str(source_account.balance)
        }, status=status.HTTP_200_OK)   

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
