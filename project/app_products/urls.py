from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CategoryViewSet, ProductViewSet, ReviewViewSet
from . import views

app_name = 'products'

router = DefaultRouter()
router.register(r'categories', CategoryViewSet, basename='category')
router.register(r'products', ProductViewSet, basename='product')
router.register(r'reviews', ReviewViewSet, basename='review')

custom_urlpatterns = [
    path('products/<slug:slug>/reviews/',
         ProductViewSet.as_view({'get': 'list', 'post': 'create_review'}),
         name='product-reviews'),
    path('products/search/',
         ProductViewSet.as_view({'get': 'list'}),
         name='product-search'),
]


urlpatterns = [
    path('api/', include(custom_urlpatterns)),
    path('', views.product_list, name='products'),
    path('create/', views.create_product, name='create_product'),
    path('<slug:slug>/', views.product_detail, name='product_detail'),
    path('<slug:slug>/delete/', views.delete_product, name='delete_product'),
    path('<slug:slug>/edit/', views.edit_product, name='edit_product'),
]
