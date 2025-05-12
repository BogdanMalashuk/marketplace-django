from django.urls import path, include

urlpatterns = [
    path('admin/', include('api.routers.admin_urls')),
    path('orders/', include('api.routers.orders_urls')),
    path('products/', include('api.routers.products_urls')),
    path('shops/', include('api.routers.shops_urls')),
    path('users/', include('api.routers.users_urls')),
]
