from rest_framework import permissions
from app_shops.models import Shop
from app_orders.models import Order

class IsShopOwnerOrReadOnly(permissions.BasePermission):
    """
    Разрешение, которое позволяет владельцу магазина редактировать только свой магазин.
    """

    def has_object_permission(self, request, view, obj):
        # Разрешить доступ на чтение всем пользователям
        if request.method in permissions.SAFE_METHODS:
            return True

        # Разрешить изменение магазина только владельцу
        if isinstance(obj, Shop):
            return obj.owner == request.user

        # Разрешить изменение товара только владельцу магазина
        if hasattr(obj, 'shop'):
            return obj.shop.owner == request.user

        return False

class IsPickupPointWorkerOrReadOnly(permissions.BasePermission):
    """
    Разрешение, которое позволяет работнику ПВЗ менять статус заказа только для своего ПВЗ.
    """

    def has_object_permission(self, request, view, obj):
        # Разрешить доступ на чтение всем пользователям
        if request.method in permissions.SAFE_METHODS:
            return True

        # Разрешить изменение статуса заказа только работнику ПВЗ
        if isinstance(obj, Order):
            return obj.pickup_point.worker == request.user

        return False

class IsSuperAdmin(permissions.BasePermission):
    """
    Разрешение, которое позволяет суперадмину иметь полный доступ.
    """

    def has_permission(self, request, view):
        return request.user.is_superuser
