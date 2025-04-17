from django.db import models
from app_shops.models import Shop

# Товар
class Product(models.Model):
    name = models.CharField(max_length=200)  # Название товара
    shop = models.ForeignKey(
        Shop,
        on_delete=models.CASCADE,
        related_name='products'
    )  # Магазин, к которому относится товар
    description = models.TextField(
        blank=True,
        null=True
    )  # Описание товара, необязательное
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )  # Цена товара
    stock = models.PositiveIntegerField(default=0)  # Количество на складе
    is_available = models.BooleanField(default=True)  # Доступен ли товар
    created_at = models.DateTimeField(auto_now_add=True)  # Время создания

    def __str__(self):
        return f"{self.name} ({self.shop.name})"

    class Meta:
        indexes = [
            models.Index(fields=['shop', 'is_available']),  # Для фильтрации доступных товаров магазина
            models.Index(fields=['price']),  # Для сортировки по цене
        ]
