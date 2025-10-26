# transactions/serializers.py
from rest_framework import serializers
from .models import Transaction
from accounts.serializers import AccountSerializer
from accounts.models import Account

class TransactionSerializer(serializers.ModelSerializer):
    account = serializers.PrimaryKeyRelatedField(queryset=Account.objects.all())
    destination_account = serializers.PrimaryKeyRelatedField(queryset=Account.objects.all(), allow_null=True, required=False)

    class Meta:
        model = Transaction
        fields = ("id", "account", "type", "amount", "timestamp", "destination_account", "description", "processed")
        read_only_fields = ("id", "timestamp", "processed")

class DepositWithdrawSerializer(serializers.Serializer):
    account = serializers.IntegerField()
    amount = serializers.DecimalField(max_digits=14, decimal_places=2)

class TransferSerializer(serializers.Serializer):
    source_account = serializers.IntegerField()
    destination_account = serializers.CharField()  # accept account_number OR id
    amount = serializers.DecimalField(max_digits=14, decimal_places=2)
