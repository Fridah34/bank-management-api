from django.db import models
from django.conf import settings
from django.utils import timezone

class AuditLog(models.Model):
    ACTION_CHOICES = [
        ("deposit", "Deposit"),
        ("withdraw", "Withdraw"),
        ("transfer", "Transfer"),
        ("loan_approve", "Loan Approval"),
        ("loan_reject", "Loan Rejection"),
        ("loan_repay", "Loan Repayment"),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name="audit_logs")
    action = models.CharField(max_length=50, choices=ACTION_CHOICES)
    description = models.TextField(default="No description provided")
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ("-created_at",)

    def __str__(self):
        return f"{self.user} - {self.action} at {self.created_at:%Y-%m-%d %H:%M}"