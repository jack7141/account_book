from django.contrib import admin
from api.bases.accounts.models import Asset

@admin.register(Asset)
class AssetAdmin(admin.ModelAdmin):
    list_display = ('email', 'amount', 'transaction')
    list_filter = ('created_at', 'updated_at')


