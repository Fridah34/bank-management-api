from django.db import models, transaction
from django.utils import timezone
from decimal import Decimal
from audit.models import AuditLog
from django.contrib.auth import get_user_model

User = get_user_model()
class Loan(models.Model):
    STATUS_CHOICES = [
        ("PENDING", "Pending"),
        ("APPROVED", "Approved"),
        ("REJECTED", "Rejected"),
        ("REPAID", "Repaid"),
    ]

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="loans",
        null=True,       # ✅ allows migration to pass safely
        blank=True
    )
    amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        help_text="The total amount requested by the user."
    )
    interest_rate = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=10.00,
        help_text="Interest rate in percentage."
    )
    duration_months = models.PositiveIntegerField(
        default=12,
        help_text="Loan repayment duration in months."
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="PENDING"
    )
    approved_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Timestamp when loan was approved."
    )
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    def approve(self, approved_by=None):
        """Mark the loan as approved."""
        self.status = "APPROVED"
        self.approved_at = timezone.now()
        self.save(update_fields=["status", "approved_at"])
        AuditLog.objects.create(
            user=self.account.user,
            action="loan_approve",
            description=f"Loan #{self.id} approved for account {self.account.account_number}"
        )

    def reject(self, approved_by=None):
        """Mark the loan as rejected."""
        self.status = "REJECTED"
        self.approved_at = timezone.now()
        self.save(update_fields=["status","approved_at"])
        AuditLog.objects.create(
            user=self.account.user,
            action="loan_reject",
            description=f"Loan #{self.id} rejected for account {self.account.account_number}"
        )

    def mark_repaid(self):
        """Mark the loan as repaid."""
        self.status = "REPAID"
        self.save(update_fields=["status"])
        AuditLog.objects.create(
            user=self.account.user,
            action="loan_repay",
            description=f"Loan #{self.id} marked as repaid for account {self.account.account_number}"
        )

    def __str__(self):
        return f"Loan #{self.id} - {self.status} - {self.amount}"

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Loan"
        verbose_name_plural = "Loans"
