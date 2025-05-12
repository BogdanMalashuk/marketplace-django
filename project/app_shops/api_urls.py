from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ShopViewSet

router = DefaultRouter()
router.register(r'', ShopViewSet, basename='shop')

urlpatterns = [
    path('', include(router.urls)),                  # GET/POST   → /api/shops/
    path('<int:pk>/activate/',   ShopViewSet.as_view({'post': 'activate'}),   name='shop-activate'),
    path('<int:pk>/deactivate/', ShopViewSet.as_view({'post': 'deactivate'}), name='shop-deactivate'),
]
