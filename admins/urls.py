from django.urls import path
from .views import AdminRegisterView, CustomTokenObtainPairView, LogoutView, AdminProfileView, UpdateProfileView, PendingWorkerListView, ApproveWorkerView, RejectWorkerView, WorkerHistoryView
from rest_framework_simplejwt.views import TokenRefreshView
from django.conf.urls.static import static
from worknest import settings


urlpatterns = [
    path('register/', AdminRegisterView.as_view(), name="admin-register"),
    path('login/', CustomTokenObtainPairView.as_view(), name="admin-login"),
    path('token/refresh/', TokenRefreshView.as_view(), name="admin-login-token"),
    path('logout/', LogoutView.as_view(), name="worker-logout"),
    path('profile/', AdminProfileView.as_view(), name='user-profile'),
    path('profile/update/', UpdateProfileView.as_view(), name='update-profile'),
    path('pending-workers/', PendingWorkerListView.as_view(), name='pending-workers'),
    path('approve-worker/<int:worker_id>/', ApproveWorkerView.as_view()),
    path('reject-worker/<int:worker_id>/', RejectWorkerView.as_view()),
    path('worker-history/', WorkerHistoryView.as_view()),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
