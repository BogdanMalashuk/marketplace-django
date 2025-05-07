from rest_framework import serializers
from django.contrib.auth.models import User
from .models import UserProfile, PickupPoints


class UserBasicSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name']
        read_only_fields = fields


class PickupPointSerializer(serializers.ModelSerializer):
    class Meta:
        model = PickupPoints
        fields = [
            'id', 'name', 'city', 'street',
            'postal_code', 'description', 'is_active'
        ]
        read_only_fields = ['id']


class UserProfileSerializer(serializers.ModelSerializer):
    user = UserBasicSerializer(read_only=True)
    pickup_point = PickupPointSerializer(read_only=True)
    role_display = serializers.CharField(
        source='get_role_display',
        read_only=True
    )

    # Write-only fields for relationships
    user_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        source='user',
        write_only=True,
        required=False
    )
    pickup_point_id = serializers.PrimaryKeyRelatedField(
        queryset=PickupPoints.objects.all(),
        source='pickup_point',
        write_only=True,
        allow_null=True,
        required=False
    )

    class Meta:
        model = UserProfile
        fields = [
            'id', 'user', 'user_id', 'phone', 'role',
            'role_display', 'pickup_point', 'pickup_point_id',
            'created_at'
        ]
        read_only_fields = ['id', 'created_at', 'role_display']
        extra_kwargs = {
            'phone': {'required': False},
            'role': {'default': 'buyer'}
        }


class UserProfileCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ['phone', 'role', 'pickup_point']
        extra_kwargs = {
            'phone': {'required': False},
            'role': {'default': 'buyer'},
            'pickup_point': {'required': False}
        }


class UserProfileUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ['phone', 'role', 'pickup_point']
        extra_kwargs = {
            'phone': {'required': False},
            'role': {'required': False},
            'pickup_point': {'required': False}
        }


class PickupPointCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = PickupPoints
        fields = [
            'name', 'city', 'street',
            'postal_code', 'description', 'is_active'
        ]
        extra_kwargs = {
            'postal_code': {'required': False},
            'description': {'required': False},
            'is_active': {'default': True}
        }


class PickupPointUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = PickupPoints
        fields = [
            'name', 'city', 'street',
            'postal_code', 'description', 'is_active'
        ]
        extra_kwargs = {
            'name': {'required': False},
            'city': {'required': False},
            'street': {'required': False},
            'postal_code': {'required': False},
            'description': {'required': False},
            'is_active': {'required': False}
        }