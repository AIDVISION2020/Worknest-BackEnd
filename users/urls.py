from django.urls import path
from .views import UserRegisterView, CustomTokenObtainPairView, LogoutView, UserProfileView, UpdateProfileView, \
    MyTicketsView
from rest_framework_simplejwt.views import TokenRefreshView
from rest_framework_simplejwt.views import TokenBlacklistView
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('register/', UserRegisterView.as_view(), name="user-register"),
    path('login/', CustomTokenObtainPairView.as_view(), name="user-login"),  # Adjust roles inside serializer
    path('token/refresh/', TokenRefreshView.as_view(), name="user-login-token"),
    path('logout/', LogoutView.as_view(), name="user-logout"),
    path('profile/', UserProfileView.as_view(), name='user-profile'),
    path('profile/update/', UpdateProfileView.as_view(), name='update-profile'),
    path('my-tickets/', MyTicketsView.as_view()),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
