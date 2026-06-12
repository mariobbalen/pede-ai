from django.contrib import admin

from .models import MenuItem, Restaurant


class MenuItemInline(admin.TabularInline):
    model = MenuItem
    extra = 1
    fields = ["name", "description", "price", "is_available"]


@admin.register(Restaurant)
class RestaurantAdmin(admin.ModelAdmin):
    list_display = ["id", "name", "is_active", "created_at"]
    search_fields = ["name"]
    inlines = [MenuItemInline]


@admin.register(MenuItem)
class MenuItemAdmin(admin.ModelAdmin):
    list_display = ["id", "name", "restaurant", "price", "is_available"]
    list_filter = ["restaurant", "is_available"]
    search_fields = ["name"]
