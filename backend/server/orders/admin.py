from django.contrib import admin

from .models import Order


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ["id", "status", "customer_name", "restaurant", "address", "price", "created_at", "updated_at"]
    list_filter = ["status", "restaurant"]
    search_fields = ["id", "address", "customer_name"]
    readonly_fields = ["id", "created_at", "updated_at", "price"]
