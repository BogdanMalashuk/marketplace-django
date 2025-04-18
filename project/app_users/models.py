from django.db import models
from django.contrib.auth.models import User

# Профиль пользователя и пункты выдачи заказов (ПВЗ).
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')  # Связь с User
    phone = models.CharField(max_length=20, blank=True, null=True)  # Телефон
    role = models.CharField(max_length=20, choices=[
        ('buyer', 'Покупатель'),
        ('seller', 'Продавец'),
        ('admin', 'Администратор'),
        ('pp_staff', 'Сотрудник ПВЗ'),
    ], default='buyer', db_index=True)  # Роль пользователя
    pickup_point = models.ForeignKey('PickupPoints', on_delete=models.SET_NULL, null=True, blank=True, related_name='staff')  # ПВЗ для pp_staff
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)  # Время создания
    def __str__(self): return f"{self.user.username}'s profile"
    class Meta:
        indexes = [models.Index(fields=['user', 'role'])]

# Пункты выдачи заказов (ПВЗ) для доставки.
class PickupPoints(models.Model):
    city = models.CharField(max_length=100, db_index=True)  # Город
    street = models.CharField(max_length=200)  # Улица
    postal_code = models.CharField(max_length=20, blank=True, null=True)  # Почтовый индекс
    description = models.TextField(blank=True, null=True)  # Описание ПВЗ
    is_active = models.BooleanField(default=True, db_index=True)  # Активность ПВЗ
    def __str__(self): return f"{self.city}, {self.street}"
    class Meta:
        indexes = [models.Index(fields=['city', 'is_active'])]
        verbose_name = 'Pickup Point'
        verbose_name_plural = 'Pickup Points'
