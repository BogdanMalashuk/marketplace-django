from rest_framework import serializers
from django.contrib.auth.models import User
from app_shops.models import Shop
from app_products.models import Category, Product, Review


class ShopSerializer(serializers.ModelSerializer):
    class Meta:
        model = Shop
        fields = ['id', 'name', 'logo']
        read_only_fields = fields


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name']
        read_only_fields = fields


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'slug', 'description']
        read_only_fields = ['id', 'slug']
        extra_kwargs = {
            'name': {'required': True, 'min_length': 2},
            'description': {'required': False}
        }


class ProductListSerializer(serializers.ModelSerializer):
    shop = ShopSerializer(read_only=True)
    category = CategorySerializer(read_only=True)
    average_rating = serializers.FloatField(read_only=True)

    class Meta:
        model = Product
        fields = [
            'id', 'name', 'slug', 'shop', 'category',
            'price', 'image', 'average_rating'
        ]
        read_only_fields = fields


class ProductSerializer(serializers.ModelSerializer):
    shop = ShopSerializer(read_only=True)
    category = CategorySerializer(read_only=True)
    average_rating = serializers.FloatField(read_only=True)
    review_count = serializers.IntegerField(read_only=True)

    shop_id = serializers.PrimaryKeyRelatedField(
        queryset=Shop.objects.all(),
        source='shop',
        write_only=True
    )
    category_id = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(),
        source='category',
        write_only=True,
        allow_null=True,
        required=False
    )

    class Meta:
        model = Product
        fields = [
            'id', 'name', 'slug', 'description', 'shop', 'shop_id',
            'category', 'category_id', 'price', 'stock', 'image',
            'created_at', 'average_rating', 'review_count'
        ]
        read_only_fields = [
            'id', 'slug', 'created_at', 'average_rating', 'review_count'
        ]
        extra_kwargs = {
            'name': {'min_length': 3},
            'price': {'min_value': 0},
            'stock': {'min_value': 0},
            'image': {'required': False}
        }


class ReviewSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    product = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Review
        fields = [
            'id', 'product', 'user', 'rating',
            'comment', 'created_at'
        ]
        read_only_fields = ['id', 'created_at', 'user', 'product']
        extra_kwargs = {
            'rating': {'min_value': 1, 'max_value': 5},
            'comment': {'required': False, 'allow_blank': True}
        }


class ReviewCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = ['product', 'rating', 'comment']
        extra_kwargs = {
            'rating': {'min_value': 1, 'max_value': 5},
            'comment': {'required': False, 'allow_blank': True}
        }

    def validate(self, data):
        # Проверка, что пользователь не оставлял отзыв на этот товар
        if Review.objects.filter(
                product=data['product'],
                user=self.context['request'].user
        ).exists():
            raise serializers.ValidationError("You have already reviewed this product.")
        return data