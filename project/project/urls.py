from django.contrib import admin
from django.urls import path, include
from django.views.generic.base import RedirectView
from django.conf import settings
from django.conf.urls.static import static

from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView,
    SpectacularRedocView,
)
from rest_framework.decorators import api_view
from rest_framework.response import Response


@api_view(['GET'])
def api_root(request):
    return Response({
        "message": "Добро пожаловать в Marketplace API",
        "endpoints": {
            "products": "/api/products/",
            "orders":   "/api/orders/",
            "shops":    "/api/shops/",
            "users":    "/api/users/",
            "admin":    "/admin/",
            "schema":   "/api/schema/",
            "swagger":  "/api/docs/",
            "redoc":    "/api/redoc/",
        }
    })


urlpatterns = [
    # Корень → редирект на API
    path('', RedirectView.as_view(url='/api/'), name='root-redirect'),

    # Админка
    path('admin/', admin.site.urls),

    # API
    path('api/', api_root, name='api-root'),
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger'),
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),

    # API endpoints через приложение "api"
    path('api/', include('api.urls')),

    # Web-маршруты (HTML-интерфейсы)
    path('products/', include(('app_products.urls', 'products'), namespace='products-web')),
    path('cart/',     include(('app_orders.urls',   'orders'),   namespace='orders-web')),
    path('shops/',    include(('app_shops.urls',    'shops'),    namespace='shops-web')),
    path('users/',    include(('app_users.urls',    'users'),    namespace='users-web')),
]

# Статика и медиа-файлы в режиме DEBUG
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

    if 'debug_toolbar' in settings.INSTALLED_APPS:
        import debug_toolbar
        urlpatterns += [path('__debug__/', include(debug_toolbar.urls))]
