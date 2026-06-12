from decimal import Decimal

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from .models import MenuItem, Restaurant

# TESTES GERADOS POR IA

class RestaurantListTests(APITestCase):
    def setUp(self):
        self.restaurant = Restaurant.objects.create(name="Burguer House")
        MenuItem.objects.create(restaurant=self.restaurant, name="X-Burguer", price=Decimal("22.90"))

    def test_list_restaurants(self):
        response = self.client.get(reverse("restaurant-list"))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["results"][0]["name"], "Burguer House")
        self.assertNotIn("menu_items", response.data["results"][0])

    def test_retrieve_restaurant_includes_menu_items(self):
        response = self.client.get(reverse("restaurant-detail", args=[self.restaurant.id]))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["menu_items"]), 1)
        self.assertEqual(response.data["menu_items"][0]["name"], "X-Burguer")

    def test_inactive_restaurants_excluded_from_list(self):
        Restaurant.objects.create(name="Hidden Place", is_active=False)

        response = self.client.get(reverse("restaurant-list"))

        names = [r["name"] for r in response.data["results"]]
        self.assertNotIn("Hidden Place", names)
