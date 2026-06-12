import pika, json
from config import RABBITMQ_HOST, QUEUES

STATUS_ICONS = {
    "confirmado":         "[confirmado]",
    "preparando":         "[preparando]",
    "aguardando_motoboy": "[aguardando_motoboy]",
    "saiu_entrega":       "[saiu_entrega]",
    "delivered":          "[delivered]",
}

def receive_update(ch, method, properties, body):
    data = json.loads(body)
    icon = STATUS_ICONS.get(data["status"], "[status]")
    print(f"{icon} [{data['pedido_id'][:8]}...] {data['mensagem']}")
    ch.basic_ack(delivery_tag=method.delivery_tag)

def receive_delivery(ch, method, properties, body):
    data = json.loads(body)
    print(f"\nPedido {data['pedido_id'][:8]}... ENTREGUE! Bom apetite!\n")
    ch.basic_ack(delivery_tag=method.delivery_tag)

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
        queue=QUEUES["entregue"][0],
        on_message_callback=receive_delivery,
    )

    print("Cliente acompanhando o pedido...")
    ch.start_consuming()

if __name__ == "__main__":
    main()

# Acompanha duas filas, o de atualização e o entregue, cada um com seu próprio callback.