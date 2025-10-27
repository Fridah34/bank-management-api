from django.contrib import admin
from .models import Loan

@admin.register(Loan)
class LoanAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'amount', 'status', 'interest_rate','duration_months','reviewed_by', 'approved_at', 'created_at')
    search_fields = ('user__username',)
    list_filter = ('status', 'created_at')

