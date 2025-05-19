from rest_framework import viewsets, permissions, status, mixins
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.filters import SearchFilter, OrderingFilter
from django.db.models import Avg, Count, Q
from django_filters.rest_framework import DjangoFilterBackend

from api.serializers.products import (
    CategorySerializer,
    ProductListSerializer,
    ProductSerializer,
    ReviewCreateSerializer,
    ReviewSerializer
)
from app_products.models import Category, Product, Review


class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Только чтение категорий.
    """
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    lookup_field = 'slug'
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['is_active']


class ProductViewSet(viewsets.ModelViewSet):
    """
    CRUD для продуктов + создание отзыва через create_review.
    Оптимизация: сразу считаем средний рейтинг и количество отзывов;
    подтягиваем shop и category.
    """
    queryset = Product.objects.annotate(
        average_rating=Avg('reviews__rating'),
        review_count=Count('reviews')
    )
    lookup_field = 'slug'
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['shop', 'category', 'is_active']
    search_fields = ['name', 'description']
    ordering_fields = ['price', 'created_at']

    def get_serializer_class(self):
        if self.action == 'list':
            return ProductListSerializer
        if self.action == 'create_review':
            return ReviewCreateSerializer
        return ProductSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        # поиск по name или description
        search = self.request.query_params.get('search')
        if search:
            qs = qs.filter(Q(name__icontains=search) | Q(description__icontains=search))
        # подтягиваем связи, чтобы не было N+1
        return qs.select_related('shop', 'category')

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def create_review(self, request, slug=None):
        """
        POST /api/products/{slug}/create_review/
        Создать отзыв к продукту.
        """
        product = self.get_object()
        if Review.objects.filter(product=product, user=request.user).exists():
            return Response(
                {'error': 'You have already reviewed this product'},
                status=status.HTTP_400_BAD_REQUEST
            )
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(product=product, user=request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class ReviewViewSet(viewsets.GenericViewSet,
                    mixins.ListModelMixin,
                    mixins.RetrieveModelMixin,
                    mixins.UpdateModelMixin,
                    mixins.DestroyModelMixin):
    """
    List, retrieve, update, destroy для отзывов.
    """
    queryset = Review.objects.select_related('user', 'product')
    serializer_class = ReviewSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['user', 'product', 'rating']

    def get_permissions(self):
        if self.action in ['update', 'partial_update', 'destroy']:
            return [permissions.IsAuthenticated()]
        return [permissions.AllowAny()]

    def check_object_permissions(self, request, obj):
        super().check_object_permissions(request, obj)
        if request.method in ['PUT', 'PATCH', 'DELETE']:
            # только автор отзыва или staff
            if obj.user != request.user and not request.user.is_staff:
                self.permission_denied(
                    request,
                    message="You can only modify your own reviews.",
                    code=status.HTTP_403_FORBIDDEN
                )
