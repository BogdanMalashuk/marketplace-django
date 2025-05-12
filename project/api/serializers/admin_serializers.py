from rest_framework import serializers
from app_admin.models import AdminUser  # Примерная модель

class AdminUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = AdminUser
        fields = '__all__'
