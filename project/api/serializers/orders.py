from rest_framework import serializers
from app_products.models import Product
from app_orders.models import Cart, CartItem, Order, OrderItem
from app_shops.models import Shop
from app_users.models import PickupPoints
from api.serializers.users import UserBasicSerializer, PickupPointSerializer
from api.serializers.products import ProductSerializer
from api.serializers.shops import ShopDetailSerializer


class CartItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)
    product_id = serializers.PrimaryKeyRelatedField(
        queryset=Product.objects.all(),
        source='product',
        write_only=True
    )

    class Meta:
        model = CartItem
        fields = ['id', 'product', 'product_id', 'quantity']
        read_only_fields = ['id', 'product']


class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)
    user = UserBasicSerializer(read_only=True)
    total_price = serializers.SerializerMethodField()

    class Meta:
        model = Cart
        fields = ['id', 'user', 'created_at', 'items', 'total_price']
        read_only_fields = fields

    def get_total_price(self, obj):
        return sum(item.product.price * item.quantity for item in obj.items.all())


class OrderItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)

    class Meta:
        model = OrderItem
        fields = ['id', 'product', 'quantity', 'price']
        read_only_fields = fields


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    user = UserBasicSerializer(read_only=True)
    shop = ShopDetailSerializer(read_only=True)
    pickup_point = PickupPointSerializer(read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    shop_id = serializers.PrimaryKeyRelatedField(
        queryset=Shop.objects.all(),
        source='shop',
        write_only=True
    )
    pickup_point_id = serializers.PrimaryKeyRelatedField(
        queryset=PickupPoints.objects.all(),
        source='pickup_point',
        write_only=True,
        allow_null=True
    )

    class Meta:
        model = Order
        fields = [
            'id', 'user', 'shop', 'shop_id', 'pickup_point', 'pickup_point_id',
            'total_price', 'status', 'status_display', 'is_paid', 'created_at',
            'status_updated_at', 'items'
        ]
        read_only_fields = [
            'id', 'user', 'total_price', 'created_at', 'status_updated_at',
            'status_display', 'items'
        ]


class OrderCreateSerializer(serializers.ModelSerializer):
    shop_id = serializers.PrimaryKeyRelatedField(
        queryset=Shop.objects.all(),
        source='shop',
        write_only=True
    )
    pickup_point_id = serializers.PrimaryKeyRelatedField(
        queryset=PickupPoints.objects.all(),
        source='pickup_point',
        write_only=True,
        allow_null=True
    )

    class Meta:
        model = Order
        fields = ['shop_id', 'pickup_point_id']
