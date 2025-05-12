from rest_framework import viewsets
from app_users.models import User
from api.serializers.users_serializers import UserSerializer

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
