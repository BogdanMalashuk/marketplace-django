from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework.authtoken.views import obtain_auth_token
from api.views.users import UserProfileViewSet, UserViewSet
from django.urls import path
from . import views
from app_orders.views import order_detail_view

app_name = 'users'

router = DefaultRouter()
router.register(r'profiles', UserProfileViewSet, basename='profile')
router.register(r'users', UserViewSet, basename='user')

auth_urlpatterns = [
    path('register/',
         UserProfileViewSet.as_view({'post': 'register'}),
         name='api-register'),
    path('login/',
         UserProfileViewSet.as_view({'post': 'login'}),
         name='api-login'),
    path('logout/',
         UserProfileViewSet.as_view({'post': 'logout'}),
         name='api-logout'),
    path('me/',
         UserProfileViewSet.as_view({'get': 'me'}),
         name='api-me'),
    path('token/', obtain_auth_token, name='api-token'),
]

urlpatterns = [
    path('', include(router.urls)),
    path('auth/', include(auth_urlpatterns)),
    path('auth/', include('rest_framework.urls', namespace='rest_framework')),
]

urlpatterns = [
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('me/', views.profile_view, name='me'),
    path('pickup-point/', views.pp_view, name='my-pp'),
    path('pickup-point/order/<int:order_id>/', order_detail_view, name='order-detail'),
]
