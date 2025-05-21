from rest_framework import generics
from api.serializers.register import RegisterSerializer
from rest_framework.permissions import AllowAny

class RegisterView(generics.CreateAPIView):
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]
