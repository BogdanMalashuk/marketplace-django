from rest_framework import serializers
from django.contrib.auth.models import User
from app_users.models import UserProfile, PickupPoints

class UserBasicSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'is_staff']

class UserProfileSerializer(serializers.ModelSerializer):
    user = UserBasicSerializer(read_only=True)
    class Meta:
        model = UserProfile
        fields = ['id', 'user', 'phone', 'role', 'pickup_point', 'created_at']

class PickupPointSerializer(serializers.ModelSerializer):
    class Meta:
        model = PickupPoints
        fields = "__all__"
