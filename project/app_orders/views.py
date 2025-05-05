from django.db import models
from django.contrib.auth.models import User
from app_products.models import Product
from app_users.models import PickupPoints
from app_shops.models import Shop

# Корзина и заказы пользователей, управление процессом покупки.
class Cart(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='cart')  # Связь с User
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)  # Время создания
    def __str__(self): return f"Cart of {self.user.username}"

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')  # Связь с корзиной
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='cart_items')  # Товар
    quantity = models.PositiveIntegerField(default=1)  # Количество
    def __str__(self): return f"{self.quantity} x {self.product.name}"
    class Meta:
        indexes = [models.Index(fields=['cart', 'product'])]

class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')  # Покупатель
    shop = models.ForeignKey(Shop, on_delete=models.CASCADE, related_name='orders')  # Магазин
    pickup_point = models.ForeignKey(PickupPoints, on_delete=models.SET_NULL, null=True, related_name='orders')  # ПВЗ
    total_price = models.DecimalField(max_digits=10, decimal_places=2, db_index=True)  # Итоговая сумма
    status = models.CharField(max_length=20, choices=[
        ('pending', 'Ожидает'),
        ('confirmed', 'Подтверждён'),
        ('shipped', 'В пути'),
        ('ready_for_pickup', 'Готов к выдаче'),
        ('delivered', 'Доставлен'),
        ('returned', 'Возвращён'),
        ('unclaimed', 'Невостребован'),
    ], default='pending', db_index=True)  # Статус заказа
    is_paid = models.BooleanField(default=False, db_index=True)  # Оплачен ли заказ
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)  # Время создания
    status_updated_at = models.DateTimeField(null=True, blank=True)  # Время изменения статуса
    def __str__(self): return f"Order #{self.id} by {self.user.username}"
    class Meta:
        indexes = [
            models.Index(fields=['user', 'status']),
            models.Index(fields=['shop', 'status']),
            models.Index(fields=['status_updated_at']),
        ]

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')  # Связь с заказом
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='order_items')  # Товар
    quantity = models.PositiveIntegerField()  # Количество
    price = models.DecimalField(max_digits=10, decimal_places=2)  # Цена на момент заказа
    def __str__(self): return f"{self.quantity} x {self.product.name} in Order #{self.order.id}"
    class Meta:
        indexes = [models.Index(fields=['order', 'product'])]
