from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import action
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate
from .models import UserProfile
from .serializers import UserProfileSerializer, UserBasicSerializer
class UserProfileViewSet(viewsets.ModelViewSet):
    queryset = UserProfile.objects.select_related('user')
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from .forms import *
from app_orders.models import Order


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserBasicSerializer
    permission_classes = [permissions.IsAdminUser]

def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            profile = UserProfile(user=user)
            profile.save()
            login(request, user)
            return redirect('products')
    else:
        form = UserRegisterForm()

    return render(request, 'users/register.html', {'form': form})


# Представление для входа
def login_view(request):
    if request.method == 'POST':
        form = UserLoginForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('products')
    else:
        form = UserLoginForm()

    def get_permissions(self):
        if self.action in ['create', 'list']:
            return [permissions.IsAdminUser()]
        return super().get_permissions()

    @action(detail=False, methods=['get'])
    def me(self, request):
        profile = request.user.profile
        serializer = self.get_serializer(profile)
        return Response(serializer.data)


    @action(detail=False, methods=['post'], permission_classes=[permissions.AllowAny])
    def register(self, request):
        serializer = UserBasicSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = User.objects.create_user(
            username=serializer.validated_data['username'],
            email=serializer.validated_data.get('email', ''),
            password=request.data['password']
        )

        UserProfile.objects.create(
            user=user,
            role=request.data.get('role', 'buyer')
        )

        return Response(
            {'status': 'user created'},
            status=status.HTTP_201_CREATED
        )

    @action(detail=False, methods=['post'], permission_classes=[permissions.AllowAny])
    def login(self, request):
        user = authenticate(
            username=request.data.get('username'),
            password=request.data.get('password')
        )

        if not user:
            return Response(
                {'error': 'Invalid credentials'},
                status=status.HTTP_400_BAD_REQUEST
            )

        token, _ = Token.objects.get_or_create(user=user)
        return Response({
            'token': token.key,
            'user_id': user.id,
            'is_staff': user.is_staff
        })

    @action(detail=False, methods=['post'])
    def logout(self, request):
        request.user.auth_token.delete()
        return Response({'status': 'logged out'})

def logout_view(request):
    logout(request)
    return redirect('products')


@login_required
def profile_view(request):
    user = request.user
    user_profile = user.profile

    user_form = UserProfileUpdateForm(instance=user)
    phone_form = PhoneForm(instance=user_profile)

    if request.method == 'POST':
        form_type = request.POST.get('form_type')

        if form_type == 'user_form':
            user_form = UserProfileUpdateForm(request.POST, instance=user)
            if user_form.is_valid():
                user_form.save()
                return redirect('me')

        elif form_type == 'phone_form':
            phone_form = PhoneForm(request.POST, instance=user_profile)
            if phone_form.is_valid():
                phone_form.save()
                return redirect('me')

    return render(request, 'users/profile.html', {
        'user_form': user_form,
        'phone_form': phone_form,
        'user_profile': user_profile,
    })


@login_required
def pp_view(request):
    profile = request.user.profile
    orders = Order.objects.filter(pickup_point=profile.pickup_point).order_by('-created_at')

    return render(request, 'users/pp.html', {
        'orders': orders,
        'pickup_point': profile.pickup_point,
    })
