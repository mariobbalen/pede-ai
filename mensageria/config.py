RABBITMQ_HOST = "localhost"
EXCHANGE_NAME = "orders"
EXCHANGE_TYPE = "topic"

QUEUES = {
    "novos":   ("pedidos_novos",       "order.created"),
    "status":  ("atualizacoes_status", "order.status.*"),
    "entregue":("pedido_entregue",     "order.delivered"),
}

DLX_EXCHANGE = "orders.dlx"
DLX_QUEUE    = "pedidos_mortos"

# onde ficam as constantes compartilhadas