from django.db import models
from app_shops.models import Shop
from django.contrib.auth.models import User

# Управление товарами, категориями и отзывами.
class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)  # Название категории
    slug = models.SlugField(max_length=100, unique=True)  # SEO-дружественный URL
    description = models.TextField(blank=True, null=True)  # Описание категории
    def __str__(self): return self.name
    class Meta:
        verbose_name = 'Category'
        verbose_name_plural = 'Categories'

class Product(models.Model):
    shop = models.ForeignKey(Shop, on_delete=models.CASCADE, related_name='products')  # Магазин
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name='products')  # Категория
    name = models.CharField(max_length=200)  # Название товара
    slug = models.SlugField(max_length=200, unique=True)  # SEO-дружественный URL
    description = models.TextField(blank=True, null=True)  # Описание товара
    price = models.DecimalField(max_digits=10, decimal_places=2, db_index=True)  # Цена
    stock = models.PositiveIntegerField(default=0)  # Количество
    image = models.ImageField(upload_to='products/images/', blank=True, null=True)  # Изображение
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)  # Время создания
    is_active = models.BooleanField(default=True, db_index=True)  # Активность товара
    def __str__(self): return self.name
    class Meta:
        indexes = [
            models.Index(fields=['shop', 'category', 'is_active']),
            models.Index(fields=['price', 'created_at']),
        ]

class Review(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews')  # Товар
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews')  # Пользователь
    rating = models.PositiveSmallIntegerField(choices=[(i, i) for i in range(1, 6)], db_index=True)  # Рейтинг 1–5
    comment = models.TextField(blank=True, null=True)  # Комментарий
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)  # Время создания
    def __str__(self): return f"Review for {self.product.name} by {self.user.username}"
    class Meta:
        indexes = [models.Index(fields=['product', 'user'])]
