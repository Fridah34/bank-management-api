# accounts/serializers.py
from rest_framework import serializers
from .models import Account

class AccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = Account
        fields = ("id", "user", "account_number", "account_type", "balance", "created_at", "updated_at")
        read_only_fields = ("id", "account_number", "balance", "created_at", "updated_at", "user")

class AccountCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Account
        fields = ("id", "account_type")

    def create(self, validated_data):
        request = self.context["request"]
        return Account.objects.create(user=request.user, **validated_data)
