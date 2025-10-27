from django.contrib import admin
from .models import Account

@admin.register(Account)
class AccountAdmin(admin.ModelAdmin):
    list_display = ('id', 'user','account_type', 'account_number', 'balance', 'created_at')
    search_fields = ('account_type', 'account_number', 'user__username')
    list_filter = ('created_at',)

