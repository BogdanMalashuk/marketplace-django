from django.db import models
from django.contrib.auth.models import User

# Магазин
class Shop(models.Model):
    name = models.CharField(max_length=100)  # Название магазина
    owner = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='shops'
    )  # Владелец магазина
    description = models.TextField(
        blank=True,
        null=True
    )  # Описание магазина, необязательное
    is_active = models.BooleanField(default=True)  # Активен ли магазин
    created_at = models.DateTimeField(auto_now_add=True)  # Время создания

    def __str__(self):
        return self.name

    class Meta:
        indexes = [
            models.Index(fields=['owner', 'is_active']),  # Для фильтрации активных магазинов владельца
        ]
