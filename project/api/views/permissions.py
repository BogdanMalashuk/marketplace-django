from rest_framework import permissions
from app_shops.models import Shop
from app_orders.models import Order
from app_users.models import UserProfile, PickupPoints


class IsShopOwnerOrReadOnly(permissions.BasePermission):
    """
    Разрешение, которое позволяет продавцу редактировать только свой магазин и товары.
    Остальным пользователям доступно только чтение.
    """

    def has_permission(self, request, view):
        # Разрешить чтение всем аутентифицированным пользователям
        if request.method in permissions.SAFE_METHODS:
            return True
        # Разрешить запись только продавцам
        return request.user.is_authenticated and request.user.profile.role == 'seller'

    def has_object_permission(self, request, view, obj):
        # Разрешить чтение всем пользователям
        if request.method in permissions.SAFE_METHODS:
            return True
        # Разрешить изменение магазина или товара только владельцу магазина
        if isinstance(obj, Shop):
            return obj.owner == request.user and request.user.profile.role == 'seller'
        if hasattr(obj, 'shop'):
            return obj.shop.owner == request.user and request.user.profile.role == 'seller'
        return False


class IsPickupPointWorkerOrReadOnly(permissions.BasePermission):
    """
    Разрешение, которое позволяет работнику ПВЗ управлять своим пунктом выдачи и
    изменять статусы заказов, связанных с этим ПВЗ. Остальным доступно только чтение.
    """

    def has_permission(self, request, view):
        # Разрешить чтение всем аутентифицированным пользователям
        if request.method in permissions.SAFE_METHODS:
            return True
        # Разрешить запись только работникам ПВЗ
        return request.user.is_authenticated and request.user.profile.role == 'pp_worker'

    def has_object_permission(self, request, view, obj):
        # Разрешить чтение всем пользователям
        if request.method in permissions.SAFE_METHODS:
            return True
        # Разрешить изменение PickupPoint, если он связан с профилем работника
        if isinstance(obj, PickupPoints):
            return obj == request.user.profile.pickup_point and request.user.profile.role == 'pp_worker'
        # Разрешить изменение статуса заказа, если он связан с PickupPoint работника
        if isinstance(obj, Order):
            return obj.pickup_point == request.user.profile.pickup_point and request.user.profile.role == 'pp_worker'
        return False


class IsAdminOrSuperuser(permissions.BasePermission):
    """
    Разрешение, которое предоставляет полный доступ администраторам (is_staff) и суперадминам (is_superuser).
    """

    def has_permission(self, request, view):
        return request.user.is_authenticated and (request.user.is_staff or request.user.is_superuser)

    def has_object_permission(self, request, view, obj):
        return request.user.is_authenticated and (request.user.is_staff or request.user.is_superuser)
