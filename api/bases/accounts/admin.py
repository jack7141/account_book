from django.contrib import admin
from api.bases.accounts.models import Asset, Category
from django import forms


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('user', 'tag', )
    list_filter = ('user', 'tag', )


@admin.register(Asset)
class AssetAdmin(admin.ModelAdmin):
    list_display = ('email', 'amount', 'trade_type')
    list_filter = ('created_at', 'updated_at')
    # def formfield_for_foreignkey(self, db_field, request, **kwargs):
    #     if db_field.attname == "trade_type_id":
    #         kwargs["queryset"] = SumUp.objects.all()
    #         kwargs["choices"] = SumUp.get_trade_types()
    #     return super().formfield_for_foreignkey(db_field, request, **kwargs)

