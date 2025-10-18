from django.shortcuts import render
from rest_framework import viewsets
from .serializers import AccountSerializer
from users.permissions import IsAdminOrStaff
from .models import Account
from rest_framework.permissions import IsAuthenticated


class AccountViewSet(viewsets.ModelViewSet):
    queryset = Account.objects.all()
    serializer_class = AccountSerializer
    
    def get_permissions(self):
        if self.action in ['create', 'update', 'destroy']:
            permission_classes = [IsAdminOrStaff]
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]
    
    def get_queryset(self):
        user = self.request.user
        if user.role in ['admin', 'staff']:
            return Account.objects.all()
        return Account.objects.filter(user=user)