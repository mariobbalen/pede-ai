from decimal import Decimal

from rest_framework import serializers

from restaurants.models import MenuItem

from .models import Order

# MODEL -> JSON


class OrderItemInputSerializer(serializers.Serializer):
    """Validates the shape of each incoming item before resolving it against the menu."""

    menu_item_id = serializers.UUIDField()
    quantity = serializers.IntegerField(min_value=1)


class OrdersSerializer(serializers.ModelSerializer):
    restaurant_name = serializers.CharField(source="restaurant.name", read_only=True)

    class Meta:
        model = Order
        fields = [
            "id",
            "restaurant",
            "restaurant_name",
            "items",
            "address",
            "latitude",
            "longitude",
            "customer_name",
            "price",
            "status",
            "status_message",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "price", "status", "status_message", "created_at", "updated_at"]

    def validate_items(self, value):
        if not isinstance(value, list) or not value:
            raise serializers.ValidationError("items must be a non-empty list.")
        validated = []
        for entry in value:
            item_serializer = OrderItemInputSerializer(data=entry)
            item_serializer.is_valid(raise_exception=True)
            validated.append(item_serializer.validated_data)
        return validated

    def create(self, validated_data):
        restaurant = validated_data["restaurant"]
        raw_items = validated_data.pop("items")

        menu_item_ids = [str(item["menu_item_id"]) for item in raw_items]
        menu_items = MenuItem.objects.filter(
            restaurant=restaurant, id__in=menu_item_ids, is_available=True
        )
        menu_items_by_id = {str(menu_item.id): menu_item for menu_item in menu_items}

        snapshot_items = []
        total = Decimal("0.00")
        for entry in raw_items:
            menu_item_id = str(entry["menu_item_id"])
            menu_item = menu_items_by_id.get(menu_item_id)
            if menu_item is None:
                raise serializers.ValidationError(
                    {"items": f"Menu item {menu_item_id} is not available for this restaurant."}
                )
            quantity = entry["quantity"]
            snapshot_items.append(
                {
                    "menu_item_id": menu_item_id,
                    "name": menu_item.name,
                    "price": str(menu_item.price),
                    "quantity": quantity,
                }
            )
            total += menu_item.price * quantity

        validated_data["items"] = snapshot_items
        validated_data["price"] = total
        return super().create(validated_data)
