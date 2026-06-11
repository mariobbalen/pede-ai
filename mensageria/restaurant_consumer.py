import pika, json, time
from config import RABBITMQ_HOST, EXCHANGE_NAME, QUEUES

STATUSES = [
    ("order.status.confirmado",         "Pedido confirmado"),
    ("order.status.preparando",         "Em preparacao"),
    ("order.status.aguardando_motoboy", "Aguardando motoboy"),
    ("order.status.saiu_entrega",       "Saiu para entrega"),
    ("order.delivered",                 "Pedido entregue"),
]

def process_order(ch, method, properties, body):
    order = json.loads(body)
    print(f"\nNovo pedido recebido: {order['pedido_id']}")
    print(f"   Itens: {', '.join(order['itens'])}")
    print(f"   Endereco: {order['endereco']}")

    try:
        for routing_key, message in STATUSES:
            time.sleep(2)

            payload = {
                "pedido_id": order["pedido_id"],
                "status":    routing_key.split(".")[-1],
                "mensagem":  message,
            }
            ch.basic_publish(
                exchange=EXCHANGE_NAME,
                routing_key=routing_key,
                body=json.dumps(payload),
                properties=pika.BasicProperties(delivery_mode=2),
            )
            print(f"   -> Publicado: {message}")

        ch.basic_ack(delivery_tag=method.delivery_tag)

    except Exception as e:
        print(f"Erro ao processar pedido: {e}")
        ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)

def main():
    credentials = pika.PlainCredentials('admin', 'admin123')
    conn = pika.BlockingConnection(pika.ConnectionParameters(host = RABBITMQ_HOST, credentials=credentials))
    ch   = conn.channel()
    ch.basic_qos(prefetch_count=1)

    queue = QUEUES["novos"][0]
    ch.basic_consume(queue=queue, on_message_callback=process_order)
    print(f"Restaurante aguardando pedidos na fila [{queue}]...")
    ch.start_consuming()

if __name__ == "__main__":
    main()