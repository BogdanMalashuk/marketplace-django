from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticatedOrReadOnly

from app_products.models import Product
from api.serializers.products_serializers import ProductSerializer


class ProductViewSet(viewsets.ModelViewSet):
    """
    ViewSet для управления продуктами:
    - list: получить список продуктов
    - retrieve: получить один продукт
    - create: создать новый продукт
    - update/partial_update: обновить продукт
    - destroy: удалить продукт
    """
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
