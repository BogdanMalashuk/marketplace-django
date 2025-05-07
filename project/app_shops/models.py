from django.db import models
from django.conf import settings
from django.contrib.auth.models import User
from django.utils.text import slugify

class BaseShop(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)
    logo = models.ImageField(
        upload_to='shops/logos/',
        default='shops/logos/default.jpg',
        blank=True,
        null=True
    )
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    is_active = models.BooleanField(default=True, db_index=True)

    class Meta:
        abstract = True

class Shop(BaseShop):
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='shops')

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    class Meta:
        indexes = [
            models.Index(fields=['owner', 'is_active']),
            models.Index(fields=['slug']),
        ]
        ordering = ['-created_at']

class ShopCreationRequest(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100)
    description = models.TextField(blank=True, null=True)
    logo = models.ImageField(upload_to='shops/logos/', blank=True, null=True)
    status = models.CharField(
        max_length=10,
        choices=[
            ('pending', 'В обработке'),
            ('approved', 'Одобрена'),
            ('rejected', 'Отклонена')
        ],
        default='pending'
    )
    response_time = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Заявка на создание магазина: {self.name} от {self.user.username}"