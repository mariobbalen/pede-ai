import os

RABBITMQ_HOST = os.environ.get("RABBITMQ_HOST", "localhost")
RABBITMQ_USER = os.environ.get("RABBITMQ_USER", "admin")
RABBITMQ_PASSWORD = os.environ.get("RABBITMQ_PASSWORD", "admin123")
EXCHANGE_NAME = "orders"
EXCHANGE_TYPE = "topic"

QUEUES = {
    "new":      ("new_orders",      "order.created"),
    "status":   ("status_updates",  "order.status.*"),
    "delivered":("order_delivered", "order.delivered"),
}

DLX_EXCHANGE = "orders.dlx"
DLX_QUEUE    = "dead_orders"

# onde ficam as constantes compartilhadas