from rest_framework import serializers
from django.contrib.auth.models import User
from app_products.models import Product
from app_users.models import PickupPoints
from app_shops.models import Shop
from app_orders.models import Cart, CartItem, Order, OrderItem

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name']
        read_only_fields = fields

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'name', 'price', 'image']
        read_only_fields = fields

class PickupPointSerializer(serializers.ModelSerializer):
    class Meta:
        model = PickupPoints
        fields = ['id', 'address', 'working_hours']
        read_only_fields = fields

class ShopSerializer(serializers.ModelSerializer):
    class Meta:
        model = Shop
        fields = ['id', 'name', 'logo']
        read_only_fields = fields

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
    user = UserSerializer(read_only=True)
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
    user = UserSerializer(read_only=True)
    shop = ShopSerializer(read_only=True)
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
    class Meta:
        model = Order
        fields = ['shop', 'pickup_point']