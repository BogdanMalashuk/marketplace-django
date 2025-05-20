from rest_framework import serializers
from django.contrib.auth.models import User
from app_shops.models import Shop

class UserBasicSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name']
        read_only_fields = fields

class ShopListSerializer(serializers.ModelSerializer):
    owner = UserBasicSerializer(read_only=True)
    product_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Shop
        fields = [
            'id', 'name', 'slug', 'owner',
            'logo', 'is_active', 'created_at', 'product_count'
        ]
        read_only_fields = fields

class ShopCreateSerializer(serializers.ModelSerializer):
    owner = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = Shop
        fields = ['name', 'description', 'logo', 'is_active', 'owner']
        extra_kwargs = {
            'logo': {'required': False},
            'is_active': {'default': True}
        }

    def validate_name(self, value):
        if len(value) < 3:
            raise serializers.ValidationError("Name must be at least 3 characters long.")
        return value

class ShopDetailSerializer(serializers.ModelSerializer):
    owner = UserBasicSerializer(read_only=True)
    product_count = serializers.IntegerField(read_only=True)
    owner_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        source='owner',
        write_only=True,
        required=False
    )

    class Meta:
        model = Shop
        fields = [
            'id', 'name', 'slug', 'description',
            'owner', 'owner_id', 'logo', 'created_at',
            'is_active', 'product_count'
        ]
        read_only_fields = ['id', 'slug', 'created_at', 'product_count']

class ShopUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Shop
        fields = ['name', 'description', 'logo', 'is_active']
        extra_kwargs = {
            'name': {'required': False, 'min_length': 3},
            'logo': {'required': False}
        }