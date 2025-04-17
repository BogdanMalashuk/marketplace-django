from django.db import models
from django.contrib.auth.models import User
from app_orders.models import PickupPoint

# Профиль пользователя для клиентов, продавцов, администраторов и сотрудников ПВЗ
class UserProfile(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='profile'
    )  # Связь 1:1 с Django User
    phone = models.CharField(
        max_length=20,
        blank=True,
        null=True
    )  # Телефон, необязательный
    role = models.CharField(
        max_length=20,
        choices=[
            ('buyer', 'Покупатель'),
            ('seller', 'Продавец'),
            ('admin', 'Администратор'),
            ('pp_staff', 'Сотрудник ПВЗ'),
        ],
        default='buyer'
    )  # Роль пользователя: клиент, продавец, админ или сотрудник ПВЗ
    pickup_point = models.ForeignKey(
        PickupPoint,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='staff',
        help_text='ПВЗ, к которому привязан сотрудник (только для роли pp_staff)'
    )  # ПВЗ для сотрудников ПВЗ, null для других ролей
    created_at = models.DateTimeField(
        auto_now_add=True
    )  # Время создания профиля

    def __str__(self):
        return f"Profile of {self.user.username}"
