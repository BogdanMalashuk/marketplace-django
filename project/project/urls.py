from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic.base import RedirectView
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView
from rest_framework.response import Response
from rest_framework.decorators import api_view


@api_view(['GET'])
def api_root(request):
    return Response({
        "message": "Добро пожаловать в Marketplace API",
        "endpoints": {
            "products": "/api/products/",
            "orders": "/api/orders/",
            "shops": "/api/shops/",
            "users": "/api/users/",
            "admin": "/admin/",
            "schema": "/api/schema/",
            "swagger": "/api/docs/",
            "redoc": "/api/redoc/"
        }
    })


urlpatterns = [
    path('', RedirectView.as_view(url='/api/')),
    path('admin/', admin.site.urls),
    path('api/', api_root, name='api-root'),

    # API endpoints
    path('api/products/', include('app_products.urls')),
    path('api/orders/', include('app_orders.urls')),
    path('api/shops/', include('app_shops.urls')),
    path('api/users/', include('app_users.urls')),

    # Documentation
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger'),
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),

    # Frontend views
    path('products/', include('app_products.urls')),
    path('users/', include('app_users.urls')),
    path('cart/', include('app_orders.urls')),
    path('shops/', include('app_shops.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

    if 'debug_toolbar' in settings.INSTALLED_APPS:
        import debug_toolbar

        urlpatterns += [path('__debug__/', include(debug_toolbar.urls))]