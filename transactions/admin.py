from django.contrib import admin
from .models import Transaction

@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('id', 'account', 'type', 'amount', 'timestamp')
    search_fields = ('account__account_number',)
    list_filter = ('type', 'timestamp')
# Register your models here.
