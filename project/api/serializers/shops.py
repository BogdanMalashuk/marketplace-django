from rest_framework import serializers
from app_shops.models import Shop

class ShopListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Shop
        fields = ['id', 'name', 'slug', 'is_active', 'product_count']

class ShopDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Shop
        fields = "__all__"

class ShopCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Shop
        fields = ['name', 'slug', 'description', 'logo']

class ShopUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Shop
        fields = ['name', 'slug', 'description', 'logo', 'is_active']
