import pika, json, uuid
from config import RABBITMQ_HOST, EXCHANGE_NAME

def place_order(items: list, address: str):
    credentials = pika.PlainCredentials('admin', 'admin123')
    conn = pika.BlockingConnection(pika.ConnectionParameters(host= RABBITMQ_HOST, credentials=credentials))
    ch   = conn.channel()

    order = {
        "pedido_id": str(uuid.uuid4()),
        "itens":     items,
        "endereco":  address,
        "status":    "criado",
    }

    ch.basic_publish(
        exchange=EXCHANGE_NAME,
        routing_key="order.created",
        body=json.dumps(order),
        properties=pika.BasicProperties(
            delivery_mode=2,
            content_type="application/json",
        ),
    )
    print(f"Pedido enviado: {order['pedido_id']}")
    conn.close()
    return order["pedido_id"]

if __name__ == "__main__":
    place_order(["X-Burguer", "Coca-Cola"], "Rua das Flores, 42")