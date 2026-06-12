import json

import pika
from django.conf import settings
from django.core.management.base import BaseCommand

from orders.models import Order

# LISTENER QUE ATUALIZA NA DB CONFORME VERIFICOU NO RABBITMQ

class Command(BaseCommand):
    help = "Consume the status and delivery queues from RabbitMQ and update orders in the database."

    def handle(self, *args, **options):
        credentials = pika.PlainCredentials(settings.RABBITMQ_USER, settings.RABBITMQ_PASSWORD)
        conn = pika.BlockingConnection(
            pika.ConnectionParameters(host=settings.RABBITMQ_HOST, credentials=credentials)
        )
        ch = conn.channel()
        ch.basic_qos(prefetch_count=1)

        ch.basic_consume(
            queue=settings.QUEUES["status"][0],
            on_message_callback=self.update_status,
        )
        ch.basic_consume(
            queue=settings.QUEUES["delivered"][0],
            on_message_callback=self.mark_delivered,
        )

        self.stdout.write(self.style.SUCCESS("Waiting for order status updates..."))
        try:
            ch.start_consuming()
        except KeyboardInterrupt:
            ch.stop_consuming()
        finally:
            conn.close()

    def update_status(self, ch, method, properties, body):
        data = json.loads(body)
        updated = Order.objects.filter(id=data["order_id"]).update(
            status=data["status"],
            status_message=data.get("message", ""),
        )
        if updated:
            self.stdout.write(f"Order {data['order_id']}: {data['status']} - {data.get('message', '')}")
        else:
            self.stdout.write(self.style.WARNING(f"Order {data['order_id']} not found."))
        ch.basic_ack(delivery_tag=method.delivery_tag)

    def mark_delivered(self, ch, method, properties, body):
        data = json.loads(body)
        updated = Order.objects.filter(id=data["order_id"]).update(
            status="delivered",
            status_message=Order.STATUS_MESSAGES["delivered"],
        )
        if updated:
            self.stdout.write(self.style.SUCCESS(f"Order {data['order_id']} delivered!"))
        else:
            self.stdout.write(self.style.WARNING(f"Order {data['order_id']} not found."))
        ch.basic_ack(delivery_tag=method.delivery_tag)
