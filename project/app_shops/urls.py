from django.urls import path, include
from rest_framework.routers import DefaultRouter
from api.views.shops import ShopViewSet
from . import views

app_name = 'shops'

# DRF API routes (относительные)
router = DefaultRouter()
router.register(r'', ShopViewSet, basename='shop')

urlpatterns = [
    # API: list/create → GET/POST  /api/shops/
    path('', include(router.urls)),
    # API: custom actions → POST  /api/shops/<pk>/activate/, /api/shops/<pk>/deactivate/
    path('<int:pk>/activate/',   ShopViewSet.as_view({'post':'activate'}),   name='shop-activate'),
    path('<int:pk>/deactivate/', ShopViewSet.as_view({'post':'deactivate'}), name='shop-deactivate'),

    # Web frontend views
    path('my-shops/',               views.my_shops_view,       name='my-shops'),
    path('my-shops/<slug:slug>/',   views.my_shop_detail,      name='shop-detail'),
    path('create/',                 views.shop_create_request, name='shop-create-request'),
    path('delete/<slug:slug>/',     views.shop_delete,         name='shop-delete'),
]
