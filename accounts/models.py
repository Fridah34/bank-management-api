# accounts/models.py
import uuid
from decimal import Decimal

from django.conf import settings
from django.db import models, transaction
from django.utils import timezone
from audit.models import AuditLog

def generate_account_number():
    # Simple but unique account number: 12 numeric characters from UUID int.
    return str(uuid.uuid4().int)[:12]


class Account(models.Model):
    ACCOUNT_SAVINGS = "savings"
    ACCOUNT_CHECKING = "checking"
    ACCOUNT_CHOICES = (
        (ACCOUNT_SAVINGS, "Savings"),
        (ACCOUNT_CHECKING, "Checking"),
    )

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="accounts")
    account_number = models.CharField(max_length=32, unique=True, default=generate_account_number)
    account_type = models.CharField(max_length=20, choices=ACCOUNT_CHOICES, default=ACCOUNT_SAVINGS)
    balance = models.DecimalField(max_digits=14, decimal_places=2, default=Decimal("0.00"))
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("-created_at",)

    def __str__(self):
        return f"{self.account_number} - {self.user.username}"

    def deposit(self, amount):
        """
        Deposit amount into this account. Returns new balance.
        Uses DB atomic section and SELECT FOR UPDATE to avoid race conditions.
        """
        from django.db import transaction  # ensure DB access
        if amount <= 0:
            raise ValueError("Deposit amount must be positive")

        with transaction.atomic():
            # lock the row
            acc = Account.objects.select_for_update().get(pk=self.pk)
            acc.balance = acc.balance + Decimal(amount)
            acc.save(update_fields=["balance", "updated_at"])
            
             # Log the action
        AuditLog.objects.create(
            user=self.user,
            action="deposit",
            description=f"Deposited {amount} to account {acc.account_number}"
        )   
        return acc.balance

    def withdraw(self, amount):
        """
        Withdraw amount from this account. Raises ValueError on insufficient funds.
        """
        if amount <= 0:
            raise ValueError("Withdrawal amount must be positive")
        with transaction.atomic():
            acc = Account.objects.select_for_update().get(pk=self.pk)
            if acc.balance < Decimal(amount):
                raise ValueError("Insufficient funds")
            acc.balance = acc.balance - Decimal(amount)
            acc.save(update_fields=["balance", "updated_at"])
            
            AuditLog.objects.create(
            user=self.user,
            action="withdraw",
            description=f"Withdrew {amount} from account {acc.account_number}"
            )
            return acc.balance
        
        def transfer(self, destination_account, amount):
            """
            Transfer amount from this account to another account.
            """
            if amount <= 0:
               raise ValueError("Transfer amount must be positive")

            if self.pk == destination_account.pk:
                raise ValueError("Cannot transfer to the same account")

            from django.db import transaction
            with transaction.atomic():
               sender = Account.objects.select_for_update().get(pk=self.pk)
               receiver = Account.objects.select_for_update().get(pk=destination_account.pk)

            if sender.balance < Decimal(amount):
                raise ValueError("Insufficient funds for transfer")

            sender.balance -= Decimal(amount)
            receiver.balance += Decimal(amount)

            sender.save(update_fields=["balance", "updated_at"])
            receiver.save(update_fields=["balance", "updated_at"])
            
             # Log sender and receiver actions
            AuditLog.objects.bulk_create([
               AuditLog(user=self.user, action="transfer",
                       description=f"Transferred {amount} to {receiver.account_number}"),
               AuditLog(user=receiver.user, action="transfer",
                       description=f"Received {amount} from {sender.account_number}")
            ])

            return sender.balance

