import uuid

from django.db import models

from restaurants.models import Restaurant


class Order(models.Model):
    # Os valores devem corresponder aos status publicados por broker/restaurant_consumer.py
    STATUS_CHOICES = [
        ("created", "Created"),
        ("confirmed", "Confirmed"),
        ("preparing", "Preparing"),
        ("awaiting_courier", "Awaiting courier"),
        ("out_for_delivery", "Out for delivery"),
        ("delivered", "Delivered"),
    ]

    # Sequencia que o restaurante percorre atraves da acao "avancar".
    STATUS_FLOW = ["created", "confirmed", "preparing", "awaiting_courier", "out_for_delivery"]

    # As mensagens seguem as mesmas usadas em broker/restaurant_consumer.py para que
    # client_consumer.py mostre o mesmo texto independente de quem publicou a atualizacao.
    STATUS_MESSAGES = {
        "created": "Pedido recebido",
        "confirmed": "Pedido confirmado",
        "preparing": "Em preparacao",
        "awaiting_courier": "Aguardando motoboy",
        "out_for_delivery": "Saiu para entrega",
        "delivered": "Pedido entregue",
    }

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    restaurant = models.ForeignKey(Restaurant, on_delete=models.PROTECT, related_name="orders")
    items = models.JSONField()
    address = models.CharField(max_length=255)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    customer_name = models.CharField(max_length=255, blank=True, default="")
    price = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    status = models.CharField(max_length=32, choices=STATUS_CHOICES, default="created")
    status_message = models.CharField(max_length=255, blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Order {self.id} ({self.status})"
