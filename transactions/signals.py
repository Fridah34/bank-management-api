# transactions/signals.py
from django.db.models.signals import post_save, pre_save, post_delete
from django.dispatch import receiver
from django.db import transaction
from decimal import Decimal
from .models import Transaction
from accounts.models import Account

@receiver(pre_save, sender=Transaction)
def _transaction_pre_save(sender, instance, **kwargs):
    """
    Cache previous amount/type for updates. We'll attach attributes on instance
    so post_save can access previous values.
    """
    if instance.pk:
        # existing transaction being updated
        try:
            old = Transaction.objects.get(pk=instance.pk)
            instance._old_amount = old.amount
            instance._old_type = old.transaction_type
        except Transaction.DoesNotExist:
            instance._old_amount = None
            instance._old_type = None
    else:
        instance._old_amount = None
        instance._old_type = None

@receiver(post_save, sender=Transaction)
def _transaction_post_save(sender, instance, created, **kwargs):
    account = instance.account

    # Use atomic block and select_for_update to prevent race conditions
    with transaction.atomic():
        acc = Account.objects.select_for_update().get(pk=account.pk)

        # If created: just apply amount
        if created:
            if instance.transaction_type == 'credit':
                acc.balance = acc.balance + instance.amount
            else:
                acc.balance = acc.balance - instance.amount
        else:
            # updated transaction: remove old effect, then apply new effect
            old_amount = getattr(instance, '_old_amount', None)
            old_type = getattr(instance, '_old_type', None)

            if old_amount is not None and old_type is not None:
                # reverse old effect
                if old_type == 'credit':
                    acc.balance = acc.balance - old_amount
                else:
                    acc.balance = acc.balance + old_amount

            # apply new effect
            if instance.transaction_type == 'credit':
                acc.balance = acc.balance + instance.amount
            else:
                acc.balance = acc.balance - instance.amount

        # Optional safety: prevent negative balance (if business rule)
        # if acc.balance < Decimal('0.00'):
        #     raise ValueError("Insufficient funds")

        acc.save()

        # store balance_after for record
        instance.balance_after = acc.balance
        # avoid recursion (saving instance would trigger signal again). update only the field bypassing signals.
        Transaction.objects.filter(pk=instance.pk).update(balance_after=acc.balance)

@receiver(post_delete, sender=Transaction)
def _transaction_post_delete(sender, instance, **kwargs):
    account = instance.account
    with transaction.atomic():
        acc = Account.objects.select_for_update().get(pk=account.pk)
        # reverse effect of deleted transaction
        if instance.transaction_type == 'credit':
            acc.balance = acc.balance - instance.amount
        else:
            acc.balance = acc.balance + instance.amount
        acc.save()
