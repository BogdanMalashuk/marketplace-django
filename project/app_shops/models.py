from django.db import models
from django.contrib.auth.models import User

# Управление магазинами продавцов.
class Shop(models.Model):
    name = models.CharField(max_length=100, unique=True)  # Название магазина
    slug = models.SlugField(max_length=100, unique=True)  # SEO-дружественный URL
    description = models.TextField(blank=True, null=True)  # Описание магазина
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='shops')  # Владелец
    logo = models.ImageField(upload_to='shops/logos/', blank=True, null=True)  # Логотип
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)  # Время создания
    is_active = models.BooleanField(default=True, db_index=True)  # Активность магазина
    def __str__(self): return self.name
    class Meta:
        indexes = [models.Index(fields=['owner', 'is_active'])]
