import pika
from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import APIException
from rest_framework.response import Response

from . import broker
from .models import Order
from .serializers import OrdersSerializer


class BrokerUnavailable(APIException):
    status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    default_detail = "Could not send the order to the message broker."
    default_code = "broker_unavailable"

class OrderViewSet(
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet,
):
    queryset = Order.objects.select_related("restaurant").all()
    serializer_class = OrdersSerializer

    # filtra os pedidos por restaurante (usado pelo painel do restaurante)
    def get_queryset(self):
        qs = super().get_queryset()
        restaurant_id = self.request.query_params.get("restaurant")
        if restaurant_id:
            qs = qs.filter(restaurant_id=restaurant_id)
        return qs

    # cria o pedido
    def perform_create(self, serializer):
        order = serializer.save(status="created", status_message=Order.STATUS_MESSAGES["created"])
        try:
            broker.publish_order_created(order)
        except pika.exceptions.AMQPError as exc:
            order.delete()
            raise BrokerUnavailable() from exc

    # usado para mandar o prox status para o broker
    def _apply_status(self, order, new_status, routing_key):
        previous_status, previous_message = order.status, order.status_message
        message = Order.STATUS_MESSAGES[new_status]

        order.status = new_status
        order.status_message = message
        order.save(update_fields=["status", "status_message", "updated_at"])

        try:
            broker.publish_status_update(order, routing_key, message)
        except pika.exceptions.AMQPError as exc:
            order.status, order.status_message = previous_status, previous_message
            order.save(update_fields=["status", "status_message", "updated_at"])
            raise BrokerUnavailable() from exc

    # avança o pedido para o proximo status
    @action(detail=True, methods=["post"], url_path="advance")
    def advance(self, request, pk=None):
        order = self.get_object()
        try:
            next_index = Order.STATUS_FLOW.index(order.status) + 1
        except ValueError:
            next_index = -1

        if next_index <= 0 or next_index >= len(Order.STATUS_FLOW):
            return Response(
                {"detail": f"Order cannot be advanced from status '{order.status}'."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        new_status = Order.STATUS_FLOW[next_index]
        self._apply_status(order, new_status, f"order.status.{new_status}")
        return Response(OrdersSerializer(order).data)

    # user confirma que recebeu o pedido
    @action(detail=True, methods=["post"], url_path="confirm-delivery")
    def confirm_delivery(self, request, pk=None):
        """Marca o pedido como entregue (pelo cliente), uma vez que esteja saindo para entrega."""
        order = self.get_object()
        if order.status != "out_for_delivery":
            return Response(
                {"detail": "Order can only be confirmed as delivered once it's out for delivery."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        self._apply_status(order, "delivered", "order.delivered")
        return Response(OrdersSerializer(order).data)
