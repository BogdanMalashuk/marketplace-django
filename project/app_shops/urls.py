from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ShopViewSet
from . import views

app_name = 'shops'

router = DefaultRouter()
router.register(r'shops', ShopViewSet, basename='shop')

urlpatterns = [
    # API endpoints
    path('api/', include(router.urls)),
    path('api/shops/<int:pk>/activate/', ShopViewSet.as_view({'post': 'activate'}), name='shop-activate'),
    path('api/shops/<int:pk>/deactivate/', ShopViewSet.as_view({'post': 'deactivate'}), name='shop-deactivate'),

    # Frontend views
    path('my-shops/', views.my_shops_view, name='my-shops'),
    path('my-shops/<slug:slug>/', views.my_shop_detail, name='shop-detail'),
    path('create/', views.shop_create_request, name='shop-create-request'),
    path('delete/<slug:slug>/', views.shop_delete, name='shop-delete'),
]