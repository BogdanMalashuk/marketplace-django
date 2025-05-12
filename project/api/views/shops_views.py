from rest_framework import viewsets
from app_shops.models import Shop
from api.serializers.shops_serializers import ShopSerializer

class ShopViewSet(viewsets.ModelViewSet):
    queryset = Shop.objects.all()
    serializer_class = ShopSerializer
