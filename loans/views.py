from django.shortcuts import render
from rest_framework import viewsets, permissions, status
from .models import Loan
from .serializers import LoanSerializer
from rest_framework.decorators import action
from rest_framework.response import Response

class IsAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and getattr(request.user, "role", "") == "admin"

class LoanViewSet(viewsets.ModelViewSet):
    queryset = Loan.objects.all().select_related("user", "reviewed_by")
    serializer_class = LoanSerializer

    def get_permissions(self):
        if self.action in ["list"]:
            return [permissions.IsAuthenticated(), IsAdmin()]
        if self.action in ["approve", "reject"]:
            return [permissions.IsAuthenticated(), IsAdmin()]
        if self.action in ["create"]:
            return [permissions.IsAuthenticated()]
        return [permissions.IsAuthenticated()]

    def perform_create(self, serializer):
        # ensure the user is set to the requester
        serializer.save(user=self.request.user)

    @action(detail=True, methods=["put"], permission_classes=[IsAdmin])
    def approve(self, request, pk=None):
        loan = self.get_object()
        try:
            loan.approve(request.user)
            return Response(LoanSerializer(loan).data)
        except Exception as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=["put"],permission_classes=[IsAdmin])
    def reject(self, request, pk=None):
        loan = self.get_object()
        try:
            loan.reject(request.user)
            return Response(LoanSerializer(loan).data)
        except Exception as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)