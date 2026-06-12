from rest_framework import mixins, viewsets

from .models import Restaurant
from .serializers import RestaurantDetailSerializer, RestaurantListSerializer


class RestaurantViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    queryset = Restaurant.objects.filter(is_active=True).prefetch_related("menu_items")

    def get_serializer_class(self):
        if self.action == "retrieve":
            return RestaurantDetailSerializer
        return RestaurantListSerializer
