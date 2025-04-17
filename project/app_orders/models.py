from django.db import models
from django.contrib.auth.models import User
from app_shops.models import Shop
from app_products.models import Product

# Пункт выдачи заказов (ПВЗ)
class PickupPoint(models.Model):
    name = models.CharField(max_length=100)  # Название ПВЗ
    city = models.CharField(max_length=100)  # Город
    address = models.CharField(max_length=200)  # Адрес
    postal_code = models.CharField(
        max_length=20,
        blank=True,
        null=True
    )  # Почтовый индекс, необязательный
    description = models.TextField(
        blank=True,
        null=True
    )  # Описание ПВЗ, необязательное
    is_active = models.BooleanField(default=True)  # Активен ли ПВЗ
    created_at = models.DateTimeField(auto_now_add=True)  # Время создания

    def __str__(self):
        return f"{self.name} ({self.city}, {self.address})"

    class Meta:
        indexes = [
            models.Index(fields=['city', 'is_active']),  # Индекс для фильтрации по городу и активности
        ]

# Корзина покупателя
class Cart(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='cart'
    )  # Связь 1:1 с пользователем
    created_at = models.DateTimeField(
        auto_now_add=True,
        db_index=True
    )  # Время создания корзины

    def __str__(self):
        return f"Cart of {self.user.username}"

# Элемент корзины
class CartItem(models.Model):
    cart = models.ForeignKey(
        Cart,
        on_delete=models.CASCADE,
        related_name='items'
    )  # Корзина, к которой относится элемент
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='cart_items'
    )  # Товар в корзине
    quantity = models.PositiveIntegerField(default=1)  # Количество товара

    def __str__(self):
        return f"{self.quantity} x {self.product.name} in cart"

# Заказ
class Order(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='orders'
    )  # Покупатель
    shop = models.ForeignKey(
        Shop,
        on_delete=models.CASCADE,
        related_name='orders'
    )  # Магазин, где сделан заказ
    pickup_point = models.ForeignKey(
        PickupPoint,
        on_delete=models.SET_NULL,
        null=True,
        related_name='orders'
    )  # ПВЗ для доставки, может стать null при удалении ПВЗ
    total_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        db_index=True
    )  # Общая стоимость заказа
    status = models.CharField(
        max_length=20,
        choices=[
            ('pending', 'Ожидает'),
            ('confirmed', 'Подтверждён'),
            ('shipped', 'Отправлен'),
            ('ready_for_pickup', 'Готов к выдаче'),
            ('delivered', 'Выдан'),
            ('returned', 'Возвращён'),
            ('unclaimed', 'Невостребован'),
        ],
        default='pending',
        db_index=True
    )  # Статус заказа
    is_paid = models.BooleanField(
        default=False,
        db_index=True
    )  # Оплачен ли заказ (True только при delivered)
    created_at = models.DateTimeField(
        auto_now_add=True,
        db_index=True
    )  # Время создания заказа
    status_updated_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text='Время последнего изменения статуса заказа'
    )  # Обновляется через сигнал при смене статуса

    def __str__(self):
        return f"Order #{self.id} by {self.user.username}"

    class Meta:
        indexes = [
            models.Index(fields=['user', 'status']),  # Для фильтрации заказов пользователя
            models.Index(fields=['shop', 'status']),  # Для фильтрации заказов магазина
            models.Index(fields=['is_paid']),  # Для фильтрации оплаченных заказов
            models.Index(fields=['status_updated_at']),  # Для поиска по времени изменения статуса
        ]

# Позиция в заказе
class OrderItem(models.Model):
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name='items'
    )  # Заказ, к которому относится позиция
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='order_items'
    )  # Товар
    quantity = models.PositiveIntegerField(default=1)  # Количество
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )  # Цена за единицу на момент заказа

    def __str__(self):
        return f"{self.quantity} x {self.product.name} in order #{self.order.id}"
