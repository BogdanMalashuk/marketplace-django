from rest_framework import viewsets, permissions, status, mixins
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Avg, Count, Q
from django_filters.rest_framework import DjangoFilterBackend

from api.serializers.products import (
    CategorySerializer, ProductListSerializer,
    ProductSerializer, ReviewSerializer,
    ReviewCreateSerializer
)
from app_products.models import Category, Product, Review


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
        if self.action == 'create_review':
            return ReviewCreateSerializer
        return ProductSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        q = self.request.query_params.get('search')
        if q:
            qs = qs.filter(Q(name__icontains=q) | Q(description__icontains=q))
        return qs.select_related('shop', 'category')

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def create_review(self, request, slug=None):
        product = self.get_object()
        if Review.objects.filter(product=product, user=request.user).exists():
            return Response({'error': 'Already reviewed'}, status=status.HTTP_400_BAD_REQUEST)
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(product=product, user=request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class ReviewViewSet(viewsets.GenericViewSet,
                    mixins.ListModelMixin,
                    mixins.RetrieveModelMixin,
                    mixins.UpdateModelMixin,
                    mixins.DestroyModelMixin):
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
            if obj.user != request.user and not request.user.is_staff:
                self.permission_denied(request, message="You can only modify your own reviews.",
                                       code=status.HTTP_403_FORBIDDEN)
