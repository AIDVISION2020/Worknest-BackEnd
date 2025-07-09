from django.urls import path
from .views import (WorkerRegisterView, CustomTokenObtainPairView, LogoutView, WorkerProfileView,
                    UpdateProfileView, WorkerListAPIView, ClosestWorkersByDistance, UploadVerificationDoc,
                    WorkerProfileMe, AllWorkerListAPIView)
from rest_framework_simplejwt.views import TokenRefreshView
from django.conf.urls.static import static
from worknest import settings


urlpatterns = [
    path('register/', WorkerRegisterView.as_view(), name="worker-register"),
    path('login/', CustomTokenObtainPairView.as_view(), name="worker-login"),
    path('token/refresh/', TokenRefreshView.as_view(), name="worker-login-token"),
    path("me/", WorkerProfileMe.as_view()),
    path('logout/', LogoutView.as_view(), name="worker-logout"),
    path('profile/', WorkerProfileView.as_view(), name='user-profile'),
    path('profile/update/', UpdateProfileView.as_view(), name='update-profile'),
    path('approved_workers_det/', WorkerListAPIView.as_view(), name='worker-list'),
    path('all_workers_det/', AllWorkerListAPIView.as_view(), name='worker-list'),
    path('closest-workers/', ClosestWorkersByDistance.as_view(), name='closest-workers'),
    path("upload-verification/<int:worker_id>/", UploadVerificationDoc.as_view(), name="upload_verification"),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
