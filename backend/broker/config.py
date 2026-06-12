RABBITMQ_HOST = "localhost"
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