from rest_framework import viewsets, permissions
from rest_framework.exceptions import ValidationError
from api.serializers.orders import CartSerializer, CartItemSerializer, OrderSerializer, OrderCreateSerializer
from app_orders.models import Cart, CartItem, Order, OrderItem
from api.views.permissions import IsPickupPointWorkerOrReadOnly, IsAdminOrSuperuser


class CartViewSet(viewsets.ModelViewSet):
    """
    CRUD для корзин. Доступно только владельцу корзины.
    """
    queryset = Cart.objects.all()
    serializer_class = CartSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user)


class CartItemViewSet(viewsets.ModelViewSet):
    """
    CRUD для элементов корзины. Доступно только владельцу корзины.
    """
    queryset = CartItem.objects.all()
    serializer_class = CartItemSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return self.queryset.filter(cart__user=self.request.user)


class OrderViewSet(viewsets.ModelViewSet):
    """
    CRUD для заказов. Работники ПВЗ могут менять статус заказов своего ПВЗ, остальные — только читать.
    Админы имеют полный доступ.
    """
    queryset = Order.objects.all()
    permission_classes = [IsPickupPointWorkerOrReadOnly | IsAdminOrSuperuser]

    def get_serializer_class(self):
        if self.action in ['create']:
            return OrderCreateSerializer
        return OrderSerializer

    def get_queryset(self):
        if self.request.user.is_staff or self.request.user.is_superuser:
            return self.queryset
        return self.queryset.filter(pickup_point__userprofile__user=self.request.user)

    def perform_create(self, serializer):
        # Получаем корзину пользователя
        try:
            cart = Cart.objects.get(user=self.request.user)
        except Cart.DoesNotExist:
            raise ValidationError("Cart is empty or does not exist.")

        # Проверяем, что корзина не пуста
        cart_items = CartItem.objects.filter(cart=cart)
        if not cart_items.exists():
            raise ValidationError("Cart is empty.")

        # Создаем заказ
        order = serializer.save(user=self.request.user)

        # Переносим товары из корзины в OrderItem
        total_price = 0
        for item in cart_items:
            OrderItem.objects.create(
                order=order,
                product=item.product,
                quantity=item.quantity,
                price=item.product.price
            )
            total_price += item.product.price * item.quantity

        # Обновляем total_price заказа
        order.total_price = total_price
        order.save()

        # Очищаем корзину
        cart_items.delete()

    def perform_update(self, serializer):
        serializer.save(status=self.request.data.get('status'))
