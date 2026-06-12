import json

import pika
from django.conf import settings


def get_connection():
    credentials = pika.PlainCredentials(settings.RABBITMQ_USER, settings.RABBITMQ_PASSWORD)
    return pika.BlockingConnection(
        pika.ConnectionParameters(host=settings.RABBITMQ_HOST, credentials=credentials)
    )


def publish_order_created(order):
    """Publish the order to the 'orders' exchange with routing key 'order.created'.

    Payload keys (order_id/items/address) match the wire format expected by
    broker/restaurant_consumer.py and must not be renamed.
    """
    conn = get_connection()
    try:
        ch = conn.channel()
        payload = {
            "order_id": str(order.id),
            "items": order.items,
            "address": order.address,
            "name": order.customer_name,
            "restaurant": order.restaurant,
            "price": float(order.price) if order.price is not None else None,
            "status": order.status,
        }
        ch.basic_publish(
            exchange=settings.EXCHANGE_NAME,
            routing_key="order.created",
            body=json.dumps(payload),
            properties=pika.BasicProperties(
                delivery_mode=2,
                content_type="application/json",
            ),
        )
    finally:
        conn.close()


def publish_status_update(order, routing_key, message):
    """Publish a status update for `order` to the 'orders' exchange.

    Payload shape ({order_id, status, message}) and routing keys
    (order.status.<status> / order.delivered) match what
    broker/restaurant_consumer.py publishes, so client_consumer.py and
    consume_status keep working unchanged regardless of who triggers the update.
    """
    conn = get_connection()
    try:
        ch = conn.channel()
        payload = {
            "order_id": str(order.id),
            "status": routing_key.split(".")[-1],
            "message": message,
        }
        ch.basic_publish(
            exchange=settings.EXCHANGE_NAME,
            routing_key=routing_key,
            body=json.dumps(payload),
            properties=pika.BasicProperties(
                delivery_mode=2,
                content_type="application/json",
            ),
        )
    finally:
        conn.close()
