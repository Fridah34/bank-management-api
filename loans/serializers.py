# loans/serializers.py
from rest_framework import serializers
from .models import Loan
from django.contrib.auth import get_user_model

User = get_user_model()

class LoanSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), default=serializers.CurrentUserDefault())
    reviewed_by = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Loan
        fields = ("id", "user", "amount", "interest_rate", "status", "created_at", "reviewed_by", "updated_at")
        read_only_fields = ("id", "status", "created_at", "reviewed_by", "updated_at")
