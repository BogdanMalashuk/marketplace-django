from rest_framework import serializers
from app_products.models import Category as CategoryModel, Product as ProductModel, Review as ReviewModel

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = CategoryModel
        fields = "__all__"

class ProductListSerializer(serializers.ModelSerializer):
    average_rating = serializers.FloatField(read_only=True)
    review_count = serializers.IntegerField(read_only=True)
    class Meta:
        model = ProductModel
        fields = ['id', 'name', 'slug', 'price', 'average_rating', 'review_count']

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductModel
        fields = "__all__"

class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReviewModel
        fields = "__all__"

class ReviewCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReviewModel
        fields = ['rating', 'comment']
