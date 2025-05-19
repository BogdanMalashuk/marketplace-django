from rest_framework import viewsets
from app_admin.models import AdminUser
from api.serializers.admin import AdminUserSerializer

class AdminUserViewSet(viewsets.ModelViewSet):
    queryset = AdminUser.objects.all()
    serializer_class = AdminUserSerializer
