from django.urls import path, include
from rest_framework.routers import DefaultRouter
from api.views.orders import CartViewSet, CartItemViewSet, OrderViewSet
from . import views

app_name = 'orders'

router = DefaultRouter()
router.register(r'carts', CartViewSet, basename='cart')
router.register(r'cart-items', CartItemViewSet, basename='cart-item')
router.register(r'orders', OrderViewSet, basename='order')

urlpatterns = [
    # API endpoints
    path('api/', include(router.urls)),
    path('api/orders/<int:pk>/cancel/', OrderViewSet.as_view({'post': 'cancel'}), name='order-cancel'),

    # Frontend views
    path('edit/', views.toggle_cart_item, name='toggle_cart_item'),
    path('remove/', views.cart_remove, name='cart_remove'),
    path('update-quantity/', views.cart_update_quantity, name='cart_update_quantity'),
    path('', views.cart_view, name='cart'),
    path('order-create/', views.order_create, name='order-create'),
    path('my-orders/', views.my_orders_view, name='my-orders'),
]