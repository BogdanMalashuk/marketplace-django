from rest_framework import viewsets
from app_orders.models import Order
from api.serializers.orders_serializers import OrderSerializer

class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
