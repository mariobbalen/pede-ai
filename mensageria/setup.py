import pika
from config import *

def setup():
    credentials = pika.PlainCredentials('admin', 'admin123')
    conn = pika.BlockingConnection(pika.ConnectionParameters(host = RABBITMQ_HOST, credentials=credentials))
    ch   = conn.channel()

    
    ch.exchange_declare(exchange=DLX_EXCHANGE, exchange_type="direct", durable=True)
    ch.queue_declare(queue=DLX_QUEUE, durable=True)
    ch.queue_bind(queue=DLX_QUEUE, exchange=DLX_EXCHANGE, routing_key=DLX_QUEUE)

    
    ch.exchange_declare(exchange=EXCHANGE_NAME, exchange_type=EXCHANGE_TYPE, durable=True)

    dlx_args = {
        "x-dead-letter-exchange":    DLX_EXCHANGE,
        "x-dead-letter-routing-key": DLX_QUEUE,
    }

    for name, (queue, routing_key) in QUEUES.items():
        ch.queue_declare(queue=queue, durable=True, arguments=dlx_args)
        ch.queue_bind(queue=queue, exchange=EXCHANGE_NAME, routing_key=routing_key)

    conn.close()
    print("Infraestrutura criada com sucesso.")

if __name__ == "__main__":
    setup()

# Declara o DXL, o exchange principal, abre a conexão (precisa ser rodado antes de qualquer coisa, se não rodar, as filas e as exchanges não existem e os scripts falham.)