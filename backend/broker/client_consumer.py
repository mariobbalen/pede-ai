import pika, json
from config import RABBITMQ_HOST, QUEUES

STATUS_ICONS = {
    "confirmed":        "[confirmed]",
    "preparing":        "[preparing]",
    "awaiting_courier": "[awaiting_courier]",
    "out_for_delivery": "[out_for_delivery]",
    "delivered":        "[delivered]",
}

# Lê o payload, busca o ícone correspondente e imprime o progresso do pedido.
def receive_update(ch, method, properties, body):
    data = json.loads(body)
    icon = STATUS_ICONS.get(data["status"], "[status]")
    print(f"{icon} [{data['order_id'][:8]}...] {data['message']}")
    ch.basic_ack(delivery_tag=method.delivery_tag)

# Callback separado para o evento de entrega
def receive_delivery(ch, method, properties, body):
    data = json.loads(body)
    print(f"\nPedido {data['order_id'][:8]}... ENTREGUE! Bom apetite!\n")
    ch.basic_ack(delivery_tag=method.delivery_tag)

# Registra 2 callbacks em filas diferentes, e fica escutando 2 ao mesmo tempo no mesmo loop
def main():
    credentials = pika.PlainCredentials('admin', 'admin123')
    conn = pika.BlockingConnection(pika.ConnectionParameters(host = RABBITMQ_HOST, credentials=credentials))
    ch   = conn.channel()
    ch.basic_qos(prefetch_count=1)

    ch.basic_consume(
        queue=QUEUES["status"][0],
        on_message_callback=receive_update,
    )
    ch.basic_consume(
        queue=QUEUES["delivered"][0],
        on_message_callback=receive_delivery,
    )

    print("Cliente acompanhando o pedido...")
    ch.start_consuming()

if __name__ == "__main__":
    main()

# Acompanha duas filas, o de atualização e o entregue, cada um com seu próprio callback.