import json
import uuid
from decimal import Decimal
from unittest.mock import MagicMock, patch

import pika
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from restaurants.models import MenuItem, Restaurant

from .management.commands.consume_status import Command
from .models import Order

# TESTES GERADOS POR IA

class BrokerMockMixin:
    """Substitui a conexão real do RabbitMQ por um mock, para que os testes não precisem de um broker rodando."""

    def setUp(self):
        super().setUp()
        self.restaurant = Restaurant.objects.create(name="Burguer House")
        self.menu_item_burger = MenuItem.objects.create(
            restaurant=self.restaurant, name="X-Burguer", price=Decimal("22.90")
        )
        self.menu_item_soda = MenuItem.objects.create(
            restaurant=self.restaurant, name="Coca-Cola", price=Decimal("6.00")
        )

        self.mock_channel = MagicMock()
        mock_connection = MagicMock()
        mock_connection.channel.return_value = self.mock_channel
        patcher = patch("orders.broker.pika.BlockingConnection", return_value=mock_connection)
        patcher.start()
        self.addCleanup(patcher.stop)

    def published_payload(self):
        _, kwargs = self.mock_channel.basic_publish.call_args
        return kwargs["routing_key"], json.loads(kwargs["body"])

    def make_order(self, **overrides):
        defaults = dict(
            restaurant=self.restaurant,
            items=[
                {
                    "menu_item_id": str(self.menu_item_burger.id),
                    "name": self.menu_item_burger.name,
                    "price": str(self.menu_item_burger.price),
                    "quantity": 1,
                }
            ],
            address="Rua A, 1",
            price=self.menu_item_burger.price,
            status="created",
            status_message=Order.STATUS_MESSAGES["created"],
        )
        defaults.update(overrides)
        return Order.objects.create(**defaults)


class OrderCreateTests(BrokerMockMixin, APITestCase):
    def test_create_order_publishes_to_broker(self):
        payload = {
            "restaurant": str(self.restaurant.id),
            "items": [
                {"menu_item_id": str(self.menu_item_burger.id), "quantity": 1},
                {"menu_item_id": str(self.menu_item_soda.id), "quantity": 2},
            ],
            "address": "Rua das Flores, 42",
            "latitude": "-23.561414",
            "longitude": "-46.655881",
            "customer_name": "Mario",
        }
        response = self.client.post(reverse("order-list"), payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        order = Order.objects.get(id=response.data["id"])
        self.assertEqual(order.status, "created")
        self.assertEqual(order.status_message, "Pedido recebido")
        self.assertEqual(order.price, Decimal("34.90"))
        self.assertEqual(order.items[0]["name"], "X-Burguer")
        self.assertEqual(order.items[0]["price"], "22.90")

        routing_key, body = self.published_payload()
        self.assertEqual(routing_key, "order.created")
        self.assertEqual(body["order_id"], str(order.id))
        self.assertEqual(body["restaurant"], "Burguer House")
        self.assertEqual(body["address"], payload["address"])
        self.assertEqual(body["status"], "created")

    def test_create_order_requires_non_empty_items(self):
        payload = {"restaurant": str(self.restaurant.id), "items": [], "address": "Rua das Flores, 42"}
        response = self.client.post(reverse("order-list"), payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Order.objects.count(), 0)

    def test_create_order_rolled_back_when_broker_unavailable(self):
        self.mock_channel.basic_publish.side_effect = pika.exceptions.AMQPConnectionError()

        payload = {
            "restaurant": str(self.restaurant.id),
            "items": [{"menu_item_id": str(self.menu_item_burger.id), "quantity": 1}],
            "address": "Rua das Flores, 42",
        }
        response = self.client.post(reverse("order-list"), payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_503_SERVICE_UNAVAILABLE)
        self.assertEqual(Order.objects.count(), 0)

    def test_create_order_rejects_unknown_menu_item_id(self):
        payload = {
            "restaurant": str(self.restaurant.id),
            "items": [{"menu_item_id": str(uuid.uuid4()), "quantity": 1}],
            "address": "Rua das Flores, 42",
        }
        response = self.client.post(reverse("order-list"), payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Order.objects.count(), 0)

    def test_create_order_rejects_menu_item_from_other_restaurant(self):
        other_restaurant = Restaurant.objects.create(name="Pizzaria Bella Napoli")
        other_item = MenuItem.objects.create(
            restaurant=other_restaurant, name="Pizza Margherita", price=Decimal("45.00")
        )

        payload = {
            "restaurant": str(self.restaurant.id),
            "items": [{"menu_item_id": str(other_item.id), "quantity": 1}],
            "address": "Rua das Flores, 42",
        }
        response = self.client.post(reverse("order-list"), payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Order.objects.count(), 0)


class OrderRetrieveTests(BrokerMockMixin, APITestCase):
    def setUp(self):
        super().setUp()
        self.order = self.make_order()

    def test_list_orders(self):
        response = self.client.get(reverse("order-list"))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(response.data["results"][0]["id"], str(self.order.id))

    def test_retrieve_order(self):
        response = self.client.get(reverse("order-detail", args=[self.order.id]))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["status"], "created")
        self.assertEqual(response.data["status_message"], "Pedido recebido")
        self.assertEqual(response.data["restaurant_name"], "Burguer House")

    def test_filter_orders_by_restaurant(self):
        other_restaurant = Restaurant.objects.create(name="Pizzaria Bella Napoli")
        Order.objects.create(
            restaurant=other_restaurant,
            items=[{"menu_item_id": str(uuid.uuid4()), "name": "Pizza Margherita", "price": "45.00", "quantity": 1}],
            address="Rua B, 2",
            price=Decimal("45.00"),
            status="created",
            status_message=Order.STATUS_MESSAGES["created"],
        )

        response = self.client.get(reverse("order-list"), {"restaurant": str(self.restaurant.id)})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(response.data["results"][0]["id"], str(self.order.id))


class OrderAdvanceTests(BrokerMockMixin, APITestCase):
    def setUp(self):
        super().setUp()
        self.order = self.make_order()

    def advance(self):
        return self.client.post(reverse("order-advance", args=[self.order.id]))

    def test_advance_progresses_through_the_full_flow(self):
        expected_steps = [
            ("confirmed", "order.status.confirmed", "Pedido confirmado"),
            ("preparing", "order.status.preparing", "Em preparacao"),
            ("awaiting_courier", "order.status.awaiting_courier", "Aguardando motoboy"),
            ("out_for_delivery", "order.status.out_for_delivery", "Saiu para entrega"),
        ]

        for expected_status, expected_routing_key, expected_message in expected_steps:
            response = self.advance()

            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(response.data["status"], expected_status)
            self.assertEqual(response.data["status_message"], expected_message)

            routing_key, body = self.published_payload()
            self.assertEqual(routing_key, expected_routing_key)
            self.assertEqual(body["order_id"], str(self.order.id))
            self.assertEqual(body["status"], expected_status)
            self.assertEqual(body["message"], expected_message)

    def test_advance_fails_once_out_for_delivery(self):
        self.order.status = "out_for_delivery"
        self.order.save(update_fields=["status"])

        response = self.advance()

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_advance_fails_once_delivered(self):
        self.order.status = "delivered"
        self.order.save(update_fields=["status"])

        response = self.advance()

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_advance_rolls_back_status_when_broker_unavailable(self):
        self.mock_channel.basic_publish.side_effect = pika.exceptions.AMQPConnectionError()

        response = self.advance()

        self.assertEqual(response.status_code, status.HTTP_503_SERVICE_UNAVAILABLE)
        self.order.refresh_from_db()
        self.assertEqual(self.order.status, "created")
        self.assertEqual(self.order.status_message, Order.STATUS_MESSAGES["created"])


class OrderConfirmDeliveryTests(BrokerMockMixin, APITestCase):
    def setUp(self):
        super().setUp()
        self.order = self.make_order(
            status="out_for_delivery",
            status_message=Order.STATUS_MESSAGES["out_for_delivery"],
        )

    def confirm(self):
        return self.client.post(reverse("order-confirm-delivery", args=[self.order.id]))

    def test_confirm_delivery_marks_order_delivered(self):
        response = self.confirm()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["status"], "delivered")
        self.assertEqual(response.data["status_message"], "Pedido entregue")

        routing_key, body = self.published_payload()
        self.assertEqual(routing_key, "order.delivered")
        self.assertEqual(body["order_id"], str(self.order.id))
        self.assertEqual(body["status"], "delivered")

    def test_confirm_delivery_fails_when_not_out_for_delivery(self):
        self.order.status = "preparing"
        self.order.save(update_fields=["status"])

        response = self.confirm()

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class ConsumirStatusCommandTests(TestCase):
    def setUp(self):
        restaurant = Restaurant.objects.create(name="Burguer House")
        menu_item = MenuItem.objects.create(restaurant=restaurant, name="X-Burguer", price=Decimal("22.90"))
        self.order = Order.objects.create(
            restaurant=restaurant,
            items=[
                {
                    "menu_item_id": str(menu_item.id),
                    "name": menu_item.name,
                    "price": str(menu_item.price),
                    "quantity": 1,
                }
            ],
            address="Rua A, 1",
            price=menu_item.price,
            status="confirmed",
            status_message=Order.STATUS_MESSAGES["confirmed"],
        )
        self.command = Command()
        self.mock_channel = MagicMock()
        self.mock_method = MagicMock(delivery_tag=1)

    def test_update_status_updates_matching_order(self):
        body = json.dumps(
            {"order_id": str(self.order.id), "status": "preparing", "message": "Em preparacao"}
        ).encode()

        self.command.update_status(self.mock_channel, self.mock_method, None, body)

        self.order.refresh_from_db()
        self.assertEqual(self.order.status, "preparing")
        self.assertEqual(self.order.status_message, "Em preparacao")
        self.mock_channel.basic_ack.assert_called_once_with(delivery_tag=1)

    def test_mark_delivered_updates_matching_order(self):
        body = json.dumps(
            {"order_id": str(self.order.id), "status": "delivered", "message": "Pedido entregue"}
        ).encode()

        self.command.mark_delivered(self.mock_channel, self.mock_method, None, body)

        self.order.refresh_from_db()
        self.assertEqual(self.order.status, "delivered")
        self.assertEqual(self.order.status_message, Order.STATUS_MESSAGES["delivered"])
        self.mock_channel.basic_ack.assert_called_once_with(delivery_tag=1)

    def test_update_status_acks_message_for_unknown_order(self):
        body = json.dumps(
            {"order_id": str(uuid.uuid4()), "status": "preparing", "message": "Em preparacao"}
        ).encode()

        self.command.update_status(self.mock_channel, self.mock_method, None, body)

        self.mock_channel.basic_ack.assert_called_once_with(delivery_tag=1)
