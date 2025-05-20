from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Count
from django_filters.rest_framework import DjangoFilterBackend

from api.serializers.shops import (
    ShopListSerializer, ShopDetailSerializer,
    ShopCreateSerializer, ShopUpdateSerializer
)
from app_shops.models import Shop
from .permissions import IsShopOwnerOrReadOnly


class ShopViewSet(viewsets.ModelViewSet):
    queryset = Shop.objects.annotate(product_count=Count('products'))
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['owner', 'is_active']
    permission_classes = [IsShopOwnerOrReadOnly]

    def get_serializer_class(self):
        mapping = {
            'create': ShopCreateSerializer,
            'list': ShopListSerializer,
            'retrieve': ShopDetailSerializer,
            'update': ShopUpdateSerializer,
            'partial_update': ShopUpdateSerializer,
        }
        return mapping.get(self.action, ShopDetailSerializer)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def activate(self, request, pk=None):
        shop = self.get_object()
        shop.is_active = True
        shop.save()
        return Response({'status': 'activated'})

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def deactivate(self, request, pk=None):
        shop = self.get_object()
        shop.is_active = False
        shop.save()
        return Response({'status': 'deactivated'})
