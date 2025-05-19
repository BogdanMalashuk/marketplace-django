from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from api.serializers.orders import (
    CartSerializer,
    CartItemSerializer,
    OrderCreateSerializer,
    OrderSerializer,
)
from app_orders.models import Cart, CartItem, Order, OrderItem


class CartViewSet(viewsets.ModelViewSet):
    """
    CRUD для корзины пользователя.
    """
    serializer_class = CartSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # возвращаем только корзину текущего пользователя
        return Cart.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class CartItemViewSet(viewsets.ModelViewSet):
    """
    CRUD для позиций в корзине.
    """
    serializer_class = CartItemSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # возвращаем только позиции корзины текущего пользователя
        return CartItem.objects.filter(cart__user=self.request.user)

    def perform_create(self, serializer):
        # если корзина не существует — создаём
        cart, _ = Cart.objects.get_or_create(user=self.request.user)
        serializer.save(cart=cart)


class OrderViewSet(viewsets.ModelViewSet):
    """
    CRUD для заказов:
    - create: создаётся из корзины
    - cancel: отмена заказа
    """
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.action == 'create':
            return OrderCreateSerializer
        return super().get_serializer_class()

    def get_queryset(self):
        # оптимизируем запрос: подтягиваем связь shop и pickup_point и детали позиций
        return (
            Order.objects
            .filter(user=self.request.user)
            .select_related('shop', 'pickup_point')
            .prefetch_related('items__product')
        )

    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        """
        POST /api/orders/{pk}/cancel/
        Отменить заказ, если он в статусе pending или confirmed.
        """
        order = self.get_object()
        # проверяем право доступа
        if order.user != request.user:
            return Response({'detail': 'Forbidden'}, status=status.HTTP_403_FORBIDDEN)
        if order.status not in ['pending', 'confirmed']:
            return Response(
                {'error': 'Cannot cancel at this stage'},
                status=status.HTTP_400_BAD_REQUEST
            )
        order.status = 'canceled'
        order.save()
        return Response({'status': 'canceled'})

    def perform_create(self, serializer):
        # создаём заказ из корзины текущего пользователя
        cart = Cart.objects.get(user=self.request.user)
        order = serializer.save(user=self.request.user)
        # создаём OrderItem пачкой для оптимизации
        items = cart.items.all()
        order_items = [
            OrderItem(
                order=order,
                product=item.product,
                quantity=item.quantity,
                price=item.product.price
            )
            for item in items
        ]
        OrderItem.objects.bulk_create(order_items)
        # очищаем корзину
        items.delete()
