from django.urls import path, include
from rest_framework.routers import DefaultRouter

#from api.views.admin import AdminUserViewSet
from api.views.users import UserViewSet, UserProfileViewSet
from api.views.shops import ShopViewSet
from api.views.products import CategoryViewSet, ProductViewSet, ReviewViewSet
from api.views.orders import CartViewSet, CartItemViewSet, OrderViewSet

router = DefaultRouter()
#router.register(r'admin/users', AdminUserViewSet, basename='admin-user')
router.register(r'users', UserViewSet, basename='user')
router.register(r'profiles', UserProfileViewSet, basename='profile')
router.register(r'shops', ShopViewSet, basename='shop')
router.register(r'categories', CategoryViewSet, basename='category')
router.register(r'products', ProductViewSet, basename='product')
router.register(r'reviews', ReviewViewSet, basename='review')
router.register(r'carts', CartViewSet, basename='cart')
router.register(r'cart-items', CartItemViewSet, basename='cart-item')
router.register(r'orders', OrderViewSet, basename='order')

urlpatterns = [
    path('', include(router.urls)),
]
