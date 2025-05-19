from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from api.serializers.orders import (
    CartSerializer, CartItemSerializer,
    OrderSerializer, OrderCreateSerializer
)
from app_orders.models import Cart, CartItem, Order, OrderItem


class CartViewSet(viewsets.ModelViewSet):
    queryset = Cart.objects.all()
    serializer_class = CartSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class CartItemViewSet(viewsets.ModelViewSet):
    queryset = CartItem.objects.all()
    serializer_class = CartItemSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return self.queryset.filter(cart__user=self.request.user)

    def perform_create(self, serializer):
        cart, _ = Cart.objects.get_or_create(user=self.request.user)
        serializer.save(cart=cart)


class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.action == 'create':
            return OrderCreateSerializer
        return super().get_serializer_class()

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user).select_related('shop', 'pickup_point').prefetch_related(
            'items__product')

    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        order = self.get_object()
        if order.user != request.user:
            return Response({'error': 'Forbidden'}, status=403)
        if order.status not in ['pending', 'confirmed']:
            return Response({'error': 'Cannot cancel at this stage'}, status=status.HTTP_400_BAD_REQUEST)
        order.status = 'canceled'
        order.save()
        return Response({'status': 'canceled'})

    def perform_create(self, serializer):
        cart = Cart.objects.get(user=self.request.user)
        order = serializer.save(user=self.request.user)
        items = cart.items.all()
        objs = [
            OrderItem(order=order, product=i.product, quantity=i.quantity, price=i.product.price)
            for i in items
        ]
        OrderItem.objects.bulk_create(objs)
        items.delete()
