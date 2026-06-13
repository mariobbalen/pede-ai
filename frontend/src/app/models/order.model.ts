export interface OrderItemInput {
  menu_item_id: string;
  quantity: number;
}

export interface OrderItemSnapshot extends OrderItemInput {
  name: string;
  price: string;
}

export type OrderStatus =
  | 'created'
  | 'confirmed'
  | 'preparing'
  | 'awaiting_courier'
  | 'out_for_delivery'
  | 'delivered';

export interface Order {
  id: string;
  restaurant: string;
  restaurant_name: string;
  items: OrderItemSnapshot[];
  address: string;
  latitude: string | null;
  longitude: string | null;
  customer_name: string;
  price: string | null;
  status: OrderStatus;
  status_message: string;
  created_at: string;
  updated_at: string;
}

export interface CreateOrderPayload {
  restaurant: string;
  items: OrderItemInput[];
  address: string;
  latitude: number;
  longitude: number;
  customer_name: string;
}

// Reflete Order.STATUS_FLOW em backend/server/orders/models.py
export const STATUS_FLOW: OrderStatus[] = [
  'created',
  'confirmed',
  'preparing',
  'awaiting_courier',
  'out_for_delivery',
];

// Reflete Order.STATUS_MESSAGES em backend/server/orders/models.py (pt-BR, exibido ao usuário)
export const STATUS_MESSAGES: Record<OrderStatus, string> = {
  created: 'Pedido recebido',
  confirmed: 'Pedido confirmado',
  preparing: 'Em preparação',
  awaiting_courier: 'Aguardando motoboy',
  out_for_delivery: 'Saiu para entrega',
  delivered: 'Pedido entregue',
};

// Texto exibido no botão "avançar" do painel do restaurante, indexado pelo status para o qual o pedido avança.
export const ADVANCE_BUTTON_LABELS: Partial<Record<OrderStatus, string>> = {
  confirmed: 'Confirmar pedido',
  preparing: 'Iniciar preparo',
  awaiting_courier: 'Pedido pronto (aguardar motoboy)',
  out_for_delivery: 'Saiu para entrega',
};
