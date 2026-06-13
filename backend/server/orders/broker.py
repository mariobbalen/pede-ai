import json

import pika
from django.conf import settings


def get_connection():
    credentials = pika.PlainCredentials(settings.RABBITMQ_USER, settings.RABBITMQ_PASSWORD)
    return pika.BlockingConnection(
        pika.ConnectionParameters(host=settings.RABBITMQ_HOST, credentials=credentials)
    )


def publish_order_created(order):
    """Publica o pedido no exchange 'orders' com a routing key 'order.created'.

    As chaves do payload (order_id/items/address) seguem o formato esperado por
    broker/restaurant_consumer.py e não devem ser renomeadas.
    """
    conn = get_connection()
    try:
        ch = conn.channel()
        payload = {
            "order_id": str(order.id),
            "items": order.items,
            "address": order.address,
            "name": order.customer_name,
            "restaurant": order.restaurant.name,
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
    """Publica uma atualização de status de `order` no exchange 'orders'.

    O formato do payload ({order_id, status, message}) e as routing keys
    (order.status.<status> / order.delivered) seguem o que
    broker/restaurant_consumer.py publica, para que client_consumer.py e
    consume_status continuem funcionando sem mudanças, independente de quem
    disparou a atualização.
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
