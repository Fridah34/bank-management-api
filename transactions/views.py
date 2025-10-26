from django.shortcuts import render
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Transaction
from .serializers import TransactionSerializer, DepositWithdrawSerializer, TransferSerializer
from accounts.models import Account
from decimal import Decimal
from rest_framework.permissions import IsAuthenticated
from django.db import transaction as db_transaction

class TransactionViewSet(viewsets.ReadOnlyModelViewSet):
    """
    list (admin) or owner transaction list via ?account=<id>
    deposit/withdraw/transfer actions are defined below.
    """
    queryset = Transaction.objects.all().select_related("account", "destination_account")
    serializer_class = TransactionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.role == "admin":
            return self.queryset
        # filter to transactions where the user is owner of the source or destination
        return self.queryset.filter(models.Q(account__user=user) | models.Q(destination_account__user=user))

    @action(detail=False, methods=["post"])
    def deposit(self, request):
        serializer = DepositWithdrawSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        acc_id = serializer.validated_data["account"]
        amount = Decimal(serializer.validated_data["amount"])
        try:
            with db_transaction.atomic():
                acc = Account.objects.select_for_update().get(pk=acc_id)
                # check ownership
                if acc.user != request.user and request.user.role != "admin":
                    return Response({"detail": "Not allowed"}, status=status.HTTP_403_FORBIDDEN)
                tx = Transaction.objects.create(account=acc, type=Transaction.TYPE_DEPOSIT, amount=amount, description="Deposit via API")
                # Processing handled by signal
                return Response(TransactionSerializer(tx).data, status=status.HTTP_201_CREATED)
        except Account.DoesNotExist:
            return Response({"detail":"Account not found"}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=["post"])
    def withdraw(self, request):
        serializer = DepositWithdrawSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        acc_id = serializer.validated_data["account"]
        amount = Decimal(serializer.validated_data["amount"])
        try:
            with db_transaction.atomic():
                acc = Account.objects.select_for_update().get(pk=acc_id)
                if acc.user != request.user and request.user.role != "admin":
                    return Response({"detail":"Not allowed"}, status=status.HTTP_403_FORBIDDEN)
                if acc.balance < amount:
                    return Response({"detail":"Insufficient funds"}, status=status.HTTP_400_BAD_REQUEST)
                tx = Transaction.objects.create(account=acc, type=Transaction.TYPE_WITHDRAWAL, amount=amount, description="Withdrawal via API")
                return Response(TransactionSerializer(tx).data, status=status.HTTP_201_CREATED)
        except Account.DoesNotExist:
            return Response({"detail":"Account not found"}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=["post"])
    def transfer(self, request):
        serializer = TransferSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        src_id = serializer.validated_data["source_account"]
        dst_ref = serializer.validated_data["destination_account"]
        amount = Decimal(serializer.validated_data["amount"])

        try:
            with db_transaction.atomic():
                src = Account.objects.select_for_update().get(pk=src_id)
                # allow lookup by account_number if a string was provided
                destination = None
                # try by id first
                try:
                    destination = Account.objects.get(pk=int(dst_ref))
                except Exception:
                    # fallback to account_number
                    destination = Account.objects.get(account_number=dst_ref)

                if src.user != request.user and request.user.role != "admin":
                    return Response({"detail":"Not allowed"}, status=status.HTTP_403_FORBIDDEN)
                if src.balance < amount:
                    return Response({"detail":"Insufficient funds"}, status=status.HTTP_400_BAD_REQUEST)

                tx = Transaction.objects.create(account=src, type=Transaction.TYPE_TRANSFER, amount=amount,
                                                destination_account=destination,
                                                description=f"Transfer to {destination.account_number}")
                return Response(TransactionSerializer(tx).data, status=status.HTTP_201_CREATED)
        except Account.DoesNotExist:
            return Response({"detail":"Account not found"}, status=status.HTTP_400_BAD_REQUEST)