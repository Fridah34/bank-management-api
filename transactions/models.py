from decimal import Decimal
from django.db import models, transaction
from django.utils import timezone
from django.db.models.signals import post_save
from django.dispatch import receiver


class Transaction(models.Model):
    TYPE_DEPOSIT = "deposit"
    TYPE_WITHDRAWAL = "withdrawal"
    TYPE_TRANSFER = "transfer"

    TYPE_CHOICES = (
        (TYPE_DEPOSIT, "Deposit"),
        (TYPE_WITHDRAWAL, "Withdrawal"),
        (TYPE_TRANSFER, "Transfer"),
    )

    # Account this transaction affects (source for transfers)
    account = models.ForeignKey(
        "accounts.Account",
        on_delete=models.CASCADE,
        related_name="transactions"
    )
    type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    amount = models.DecimalField(max_digits=14, decimal_places=2)
    timestamp = models.DateTimeField(default=timezone.now)

    # For transfers, the destination account (nullable)
    destination_account = models.ForeignKey(
        "accounts.Account",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="incoming_transactions"
    )

    description = models.CharField(max_length=255, blank=True)
    processed = models.BooleanField(default=False)

    class Meta:
        ordering = ("-timestamp",)

    def __str__(self):
        return f"{self.type} {self.amount} on {self.account.account_number}"

    def clean_amount(self):
        if self.amount <= Decimal("0.00"):
            raise ValueError("Transaction amount must be positive")

    def process(self):
        """
        Apply the transaction to account balances safely.
        Called automatically after save.
        """
        from accounts.models import Account  # local import to avoid circular imports

        if self.processed:
            return  # already applied

        if self.amount <= Decimal("0.00"):
            raise ValueError("Transaction amount must be positive")

        with transaction.atomic():
            # Lock involved account rows
            source = Account.objects.select_for_update().get(pk=self.account_id)

            if self.type == self.TYPE_DEPOSIT:
                source.balance += self.amount
                source.save(update_fields=["balance", "updated_at"])

            elif self.type == self.TYPE_WITHDRAWAL:
                if source.balance < self.amount:
                    raise ValueError("Insufficient funds for withdrawal")
                source.balance -= self.amount
                source.save(update_fields=["balance", "updated_at"])

            elif self.type == self.TYPE_TRANSFER:
                if not self.destination_account_id:
                    raise ValueError("Destination account required for transfers")
                destination = Account.objects.select_for_update().get(pk=self.destination_account_id)

                if source.balance < self.amount:
                    raise ValueError("Insufficient funds for transfer")

                source.balance -= self.amount
                destination.balance += self.amount
                source.save(update_fields=["balance", "updated_at"])
                destination.save(update_fields=["balance", "updated_at"])
            else:
                raise ValueError("Unknown transaction type")

            # Mark as processed
            self.processed = True
            self.save(update_fields=["processed"])


# ✅ Post-save signal defined OUTSIDE the class
@receiver(post_save, sender=Transaction)
def post_save_transaction(sender, instance: Transaction, created, **kwargs):
    """
    Automatically process transactions immediately after creation.
    """
    if created and not instance.processed:
        try:
            instance.process()
        except Exception as e:
            # You can replace this with logging later
            raise e
