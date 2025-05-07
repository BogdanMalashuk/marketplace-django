from rest_framework import viewsets, status, permissions, mixins
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Avg, Count, Q
from django_filters.rest_framework import DjangoFilterBackend
from .models import Category, Product, Review
from .serializers import (
    CategorySerializer,
    ProductListSerializer,
    ProductSerializer,
    ReviewSerializer,
    ReviewCreateSerializer
)


class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    lookup_field = 'slug'
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['is_active']


class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.annotate(
        average_rating=Avg('reviews__rating'),
        review_count=Count('reviews')
    )
    lookup_field = 'slug'
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['shop', 'category', 'is_active']

    def get_serializer_class(self):
        if self.action == 'list':
            return ProductListSerializer
        elif self.action == 'create_review':
            return ReviewCreateSerializer
        return ProductSerializer

    def get_queryset(self):
        queryset = super().get_queryset()

        # Комплексный поиск
        search_query = self.request.query_params.get('search')
        if search_query:
            queryset = queryset.filter(
                Q(name__icontains=search_query) |
                Q(description__icontains=search_query)
            )

        return queryset.select_related('shop', 'category')

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def create_review(self, request, slug=None):
        product = self.get_object()
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Проверка на существующий отзыв
        if Review.objects.filter(product=product, user=request.user).exists():
            return Response(
                {'error': 'You have already reviewed this product'},
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer.save(product=product, user=request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class ReviewViewSet(mixins.RetrieveModelMixin,
                    mixins.UpdateModelMixin,
                    mixins.DestroyModelMixin,
                    mixins.ListModelMixin,
                    viewsets.GenericViewSet):
    serializer_class = ReviewSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['user', 'product', 'rating']

    def get_queryset(self):
        return Review.objects.select_related('user', 'product')

    def get_permissions(self):
        if self.action in ['update', 'partial_update', 'destroy']:
            return [permissions.IsAuthenticated()]
        return [permissions.AllowAny()]

    def check_object_permissions(self, request, obj):
        super().check_object_permissions(request, obj)
        if request.method in ['PUT', 'PATCH', 'DELETE']:
            if obj.user != request.user and not request.user.is_staff:
                self.permission_denied(
                    request,
                    message="You can only modify your own reviews.",
                    code=status.HTTP_403_FORBIDDEN
                )


from django.shortcuts import render, get_object_or_404, redirect
from .models import Product
from app_orders.models import Cart, CartItem
from app_shops.models import Shop
from .forms import ProductForm
from django.contrib.auth.decorators import login_required
from django.db.models import Q


def product_list(request):
    query = request.GET.get('q')  # Приводим запрос к нижнему регистру
    products = Product.objects.all()

    if query:
        products = products.filter(
            Q(name__icontains=query) |
            Q(description__icontains=query) |
            Q(slug__icontains=query) |
            Q(category__name__icontains=query) |
            Q(shop__name__icontains=query)
        ).distinct()

    return render(request, 'products/products.html', {'products': products, 'query': query})


def product_detail(request, slug):
    product = Product.objects.get(slug=slug)
    in_cart = False
    is_owner = product.shop.owner == request.user

    if request.user.is_authenticated:
        cart, _ = Cart.objects.get_or_create(user=request.user)
        in_cart = CartItem.objects.filter(cart=cart, product=product).exists()

    return render(request, 'products/product_detail.html', {
        'product': product,
        'in_cart': in_cart,
        'is_owner': is_owner,
    })


@login_required
def delete_product(request, slug):
    product = get_object_or_404(Product, slug=slug)

    if product.shop.owner != request.user:
        return redirect('product_detail', slug=slug)

    if request.method == 'POST':
        product.delete()
        shop_slug = product.shop.slug
        return redirect('shop-detail', slug=shop_slug)

    return redirect('product_detail', slug=slug)


@login_required()
def edit_product(request, slug):
    product = get_object_or_404(Product, slug=slug)

    if product.shop.owner != request.user:
        referer = request.META.get('HTTP_REFERER')
        return redirect(referer)

    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            return redirect('shop-detail', slug=product.shop.slug)
    else:
        form = ProductForm(instance=product)

    return render(request, 'products/product_edit.html', {'form': form, 'product': product})


@login_required
def create_product(request):
    shop_slug = request.GET.get('shop')
    shop = get_object_or_404(Shop, slug=shop_slug)

    if shop.owner != request.user:
        return redirect('shop-detail', slug=shop.slug)

    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save(commit=False)
            product.shop = shop
            product.save()
            return redirect('shop-detail', slug=shop.slug)
    else:
        form = ProductForm()

    return render(request, 'products/product_create.html', {'form': form, 'shop': shop})
