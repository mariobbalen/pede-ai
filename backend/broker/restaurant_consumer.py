# APENAS PARA TESTAR O FLUXO

import pika, json, time
from config import RABBITMQ_HOST, EXCHANGE_NAME, QUEUES

STATUSES = [
    ("order.status.confirmed",         "Pedido confirmado"),
    ("order.status.preparing",         "Em preparacao"),
    ("order.status.awaiting_courier",  "Aguardando motoboy"),
    ("order.status.out_for_delivery",  "Saiu para entrega"),
    ("order.delivered",                "Pedido entregue"),
]

# lê o pedido na fila, simula o ciclo de vida, publicando 5 atualizações, e só da o ack no final
def process_order(ch, method, properties, body):
    order = json.loads(body)
    print(f"\nNovo pedido recebido: {order['order_id']}")
    items_text = ", ".join(f"{item['quantity']}x {item['name']}" for item in order['items'])
    print(f"   Itens: {items_text}")
    print(f"   Endereco: {order['address']}")

    try:
        for routing_key, message in STATUSES:
            time.sleep(2)

            payload = {
                "order_id": order["order_id"],
                "status":   routing_key.split(".")[-1],
                "message":  message,
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

# define prefetch para não receber um segundo pedido antes de terminar o atual.
def main():
    credentials = pika.PlainCredentials('admin', 'admin123')
    conn = pika.BlockingConnection(pika.ConnectionParameters(host = RABBITMQ_HOST, credentials=credentials))
    ch   = conn.channel()
    ch.basic_qos(prefetch_count=1)

    queue = QUEUES["new"][0]
    ch.basic_consume(queue=queue, on_message_callback=process_order)
    print(f"Restaurante aguardando pedidos na fila [{queue}]...")
    ch.start_consuming()

if __name__ == "__main__":
    main()

# pega uma lista de 5 atualizações, e para cada uma, ele espera 2 segundos para simular o tempo necessário. Logo, ele monta um payload e entrega para a central de distribuição. 