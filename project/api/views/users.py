from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.views.decorators.csrf import csrf_exempt
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from api.serializers.users import (
    UserBasicSerializer, UserProfileSerializer, ShopSerializer,
    ProductSerializer, PickupPointSerializer, OrderSerializer
)
from app_users.models import UserProfile, PickupPoints
from app_shops.models import Shop, Product
from app_orders.models import Order
from api.permissions import (
    IsShopOwnerOrReadOnly, IsPickupPointWorkerOrReadOnly, IsAdminOrSuperuser
)


class UserViewSet(viewsets.ModelViewSet):
    """
    CRUD для модели User (админский доступ).
    """
    queryset = User.objects.all()
    serializer_class = UserBasicSerializer
    permission_classes = [permissions.IsAdminUser]


class UserProfileViewSet(viewsets.ModelViewSet):
    """
    Профиль, регистрация, логин, логаут.
    """
    queryset = UserProfile.objects.select_related('user')
    serializer_class = UserProfileSerializer

    def get_permissions(self):
        if self.action in ['register', 'login']:
            return [permissions.AllowAny()]
        if self.action in ['me', 'logout']:
            return [permissions.IsAuthenticated()]
        return [permissions.IsAdminUser()]

    @action(detail=False, methods=['post'], permission_classes=[permissions.AllowAny])
    @csrf_exempt
    def register(self, request):
        serializer = UserBasicSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        user = serializer.save()
        UserProfile.objects.create(user=user, role=request.data.get('role', 'buyer'))
        return Response({'status': 'user created'}, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['post'], permission_classes=[permissions.AllowAny])
    @csrf_exempt
    def login(self, request):
        user = authenticate(
            username=request.data.get('username'),
            password=request.data.get('password')
        )
        if not user:
            return Response({'error': 'Invalid credentials'}, status=status.HTTP_400_BAD_REQUEST)
        token, _ = Token.objects.get_or_create(user=user)
        return Response({'token': token.key, 'user_id': user.id, 'is_staff': user.is_staff})

    @action(detail=False, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def logout(self, request):
        request.user.auth_token.delete()
        return Response({'status': 'logged out'})

    @action(detail=False, methods=['get'], permission_classes=[permissions.IsAuthenticated])
    def me(self, request):
        profile = request.user.profile
        serializer = self.get_serializer(profile)
        return Response(serializer.data)


class ShopViewSet(viewsets.ModelViewSet):
    """
    CRUD для магазинов. Продавцы могут редактировать свои магазины, остальные — только читать.
    Админы имеют полный доступ.
    """
    queryset = Shop.objects.all()
    serializer_class = ShopSerializer
    permission_classes = [IsShopOwnerOrReadOnly | IsAdminOrSuperuser]

    def get_queryset(self):
        if self.request.user.is_staff or self.request.user.is_superuser:
            return self.queryset
        return self.queryset.filter(owner=self.request.user)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class ProductViewSet(viewsets.ModelViewSet):
    """
    CRUD для товаров. Продавцы могут управлять товарами в своих магазинах, остальные — только читать.
    Админы имеют полный доступ.
    """
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [IsShopOwnerOrReadOnly | IsAdminOrSuperuser]

    def get_queryset(self):
        if self.request.user.is_staff or self.request.user.is_superuser:
            return self.queryset
        return self.queryset.filter(shop__owner=self.request.user)

    def perform_create(self, serializer):
        shop = Shop.objects.get(id=self.request.data.get('shop'), owner=self.request.user)
        serializer.save(shop=shop)


class PickupPointViewSet(viewsets.ModelViewSet):
    """
    CRUD для пунктов выдачи. Работники ПВЗ могут управлять своим ПВЗ, остальные — только читать.
    Админы имеют полный доступ.
    """
    queryset = PickupPoints.objects.all()
    serializer_class = PickupPointSerializer
    permission_classes = [IsPickupPointWorkerOrReadOnly | IsAdminOrSuperuser]

    def get_queryset(self):
        if self.request.user.is_staff or self.request.user.is_superuser:
            return self.queryset
        return self.queryset.filter(userprofile__user=self.request.user)


class OrderViewSet(viewsets.ModelViewSet):
    """
    CRUD для заказов. Работники ПВЗ могут менять статус заказов своего ПВЗ, остальные — только читать.
    Админы имеют полный доступ.
    """
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [IsPickupPointWorkerOrReadOnly | IsAdminOrSuperuser]

    def get_queryset(self):
        if self.request.user.is_staff or self.request.user.is_superuser:
            return self.queryset
        return self.queryset.filter(pickup_point__userprofile__user=self.request.user)

    def perform_update(self, serializer):
        serializer.save(status=self.request.data.get('status'))
