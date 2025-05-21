from rest_framework import viewsets, permissions
from api.serializers.products import CategorySerializer, ProductSerializer, ReviewSerializer, ReviewCreateSerializer
from app_products.models import Category, Product, Review
from api.views.permissions import IsShopOwnerOrReadOnly, IsAdminOrSuperuser


class CategoryViewSet(viewsets.ModelViewSet):
    """
    CRUD для категорий. Доступно для админов, остальным — только чтение.
    """
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [permissions.IsAdminUser]


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
        shop = Shop.objects.get(id=self.request.data.get('shop_id'), owner=self.request.user)
        serializer.save(shop=shop)


class ReviewViewSet(viewsets.ModelViewSet):
    """
    CRUD для отзывов. Доступно для пользователей, остальные — только читать.
    """
    queryset = Review.objects.all()
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_serializer_class(self):
        if self.action in ['create']:
            return ReviewCreateSerializer
        return ReviewSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user, product_id=self.request.data.get('product'))
