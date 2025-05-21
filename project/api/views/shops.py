from rest_framework import viewsets
from api.serializers.shops import ShopCreateSerializer, ShopDetailSerializer, ShopUpdateSerializer
from app_shops.models import Shop
from api.views.permissions import IsShopOwnerOrReadOnly, IsAdminOrSuperuser


class ShopViewSet(viewsets.ModelViewSet):
    """
    CRUD для магазинов. Продавцы могут редактировать свои магазины, остальные — только читать.
    Админы имеют полный доступ.
    """
    queryset = Shop.objects.all()
    permission_classes = [IsShopOwnerOrReadOnly | IsAdminOrSuperuser]

    def get_serializer_class(self):
        if self.action in ['create']:
            return ShopCreateSerializer
        if self.action in ['update', 'partial_update']:
            return ShopUpdateSerializer
        return ShopDetailSerializer

    def get_queryset(self):
        if self.request.user.is_staff or self.request.user.is_superuser:
            return self.queryset
        return self.queryset.filter(owner=self.request.user)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)
