from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Count
from django_filters.rest_framework import DjangoFilterBackend
from .models import Shop
from .serializers import (
    ShopListSerializer,
    ShopCreateSerializer,
    ShopDetailSerializer,
    ShopUpdateSerializer
)
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .forms import ShopCreationRequestForm
import os

class ShopViewSet(viewsets.ModelViewSet):
    queryset = Shop.objects.annotate(product_count=Count('products'))
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['owner', 'is_active']

    def get_serializer_class(self):
        return {
            'create': ShopCreateSerializer,
            'list': ShopListSerializer,
            'retrieve': ShopDetailSerializer,
            'update': ShopUpdateSerializer,
            'partial_update': ShopUpdateSerializer,
        }.get(self.action, ShopDetailSerializer)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    def check_object_permissions(self, request, obj):
        super().check_object_permissions(request, obj)
        if request.method in ['PUT', 'PATCH', 'DELETE']:
            if obj.owner != request.user and not request.user.is_staff:
                self.permission_denied(
                    request,
                    message="You do not have permission to perform this action.",
                    code=status.HTTP_403_FORBIDDEN
                )

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def activate(self, request, pk=None):
        shop = self.get_object()
        shop.is_active = True
        shop.save()
        return Response({'status': 'shop activated'})

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def deactivate(self, request, pk=None):
        shop = self.get_object()
        shop.is_active = False
        shop.save()
        return Response({'status': 'shop deactivated'})


def my_shops_view(request):
    shops = Shop.objects.filter(owner=request.user)
    return render(request, 'shops/shops.html', {'shops': shops})


def my_shop_detail(request, slug):
    shop = get_object_or_404(Shop, slug=slug)
    products = shop.products.all()  # related_name='products' в ForeignKey
    return render(request, 'shops/shop_detail.html', {
        'shop': shop,
        'products': products
    })


def shop_create_request(request):
    if request.method == 'POST':
        form = ShopCreationRequestForm(request.POST, request.FILES)
        if form.is_valid():
            shop_request = form.save(commit=False)
            shop_request.user = request.user
            shop_request.save()
            return redirect('my-shops')
    else:
        form = ShopCreationRequestForm()

    return render(request, 'shops/shop_create_request.html', {'form': form})


@login_required
def shop_delete(request, slug):
    shop = get_object_or_404(Shop, slug=slug)

    if shop.owner != request.user:
        return redirect('my-shops')

    if request.method == 'POST':
        if shop.logo:
            logo_path = shop.logo.path
            if os.path.isfile(logo_path):
                os.remove(logo_path)

        shop.delete()
        return redirect('my-shops')

    shops = Shop.objects.all()
    return render(request, 'shops/shops.html', {'shops': shops})
