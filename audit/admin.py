from django.contrib import admin
from .models import AuditLog

@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'action', 'created_at')
    search_fields = ('user__username', 'action')
    list_filter = ('created_at',)
# Register your models here.
