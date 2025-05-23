from django.urls import path
from . import views

urlpatterns = [
    path('edit/', views.toggle_cart_item, name='toggle_cart_item'),
    path('remove/', views.cart_remove, name='cart_remove'),
    path('update-quantity/', views.cart_update_quantity, name='cart_update_quantity'),
    path('', views.cart_view, name='cart'),
    path('order-create/', views.order_create, name='order-create'),
    path('my-orders/', views.user_orders_view, name='my-orders'),
    path('my-orders/<int:order_id>/', views.user_order_detail_view, name='user-order-detail'),
]
