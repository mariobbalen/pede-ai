import pika, json, uuid, sys
from pathlib import Path
from config import RABBITMQ_HOST, RABBITMQ_USER, RABBITMQ_PASSWORD, EXCHANGE_NAME
 
# Abre o arquivo JSON e garante que o retorno sempre seja uma lista.
def load_orders(filepath: str) -> list:
    path = Path(filepath)
    if not path.exists():
        print(f"Arquivo não encontrado: {filepath}")
        sys.exit(1)
 
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
 
    
    if isinstance(data, dict):
        data = [data]
 
    return data
 
# Monta o dicionário do pedido, gera um UUID, e publica no exchange com a routing key "order.created".
def place_order(ch, items: list, address: str) -> str:
    order = {
        "order_id": str(uuid.uuid4()),
        "items":    items,
        "address":  address,
        "status":   "created",
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
    print(f"Pedido enviado: {order['order_id']}  |  {items}  |  {address}")
    return order["order_id"]
 
# Abre a conexão, carrega os pedidos e itera sobre eles, chamando o place_order para cada válido.
def main():
    filepath = sys.argv[1] if len(sys.argv) > 1 else "orders.json"
    orders = load_orders(filepath)
 
    credentials = pika.PlainCredentials(RABBITMQ_USER, RABBITMQ_PASSWORD)
    conn = pika.BlockingConnection(
        pika.ConnectionParameters(host=RABBITMQ_HOST, credentials=credentials)
    )
    ch = conn.channel()
 
    for order in orders:
        items    = order.get("items", [])
        address = order.get("address", "")
        name = order.get ("name", "")
        restaurant = order.get("restaurant", "")
        price = order.get("price", "")
        status = order.get("status", "")
 
        if not items or not address:
            print(f"Pedido ignorado (campos faltando): {order}")
            continue
 
        place_order(ch, items, address)
 
    conn.close()
    print(f"\n{len(orders)} pedido(s) enviado(s).")
 
 
if __name__ == "__main__":
    main()

# Lê o arquivo JSON, cria um dicionario para cada pedido com UUID novo, e publica no exchange orders.