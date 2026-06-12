from rest_framework import serializers

from .models import Order

# MODEL -> JSON

class OrdersSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = [
            "id",
            "items",
            "address",
            "customer_name",
            "restaurant",
            "price",
            "status",
            "status_message",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "status", "status_message", "created_at", "updated_at"]

    def validate_items(self, value):
        if not isinstance(value, list) or not value:
            raise serializers.ValidationError("items must be a non-empty list.")
        return value
