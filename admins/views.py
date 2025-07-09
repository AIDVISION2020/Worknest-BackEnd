from rest_framework_simplejwt.views import TokenObtainPairView

from workers.models import CustomWorker
from .serializers import RegisterSerializer, CustomTokenObtainPairSerializer, AdminUpdateSerializer, AdminProfileSerializer, CustomWorkerSerializer
from rest_framework_simplejwt.tokens import RefreshToken, TokenError
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from .models import CustomAdmin
from rest_framework import generics, permissions


class RoleBasedRegisterView(APIView):
    role = None  # Set this in the URL mapping

    def post(self, request):
        data = request.data.copy()
        data['role'] = self.role

        serializer = RegisterSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response({'message': f'{self.role.capitalize()} registered successfully'}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AdminRegisterView(RoleBasedRegisterView):
    role = 'admin'


class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer


class LogoutView(APIView):
    def post(self, request):
        try:
            refresh_token = request.data["refresh"]
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response({"detail": "Logout successful"}, status=status.HTTP_205_RESET_CONTENT)
        except TokenError as e:
            return Response({"error": "Token is invalid or expired"}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class AdminProfileView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        try:
            admin = request.user.admin_profile  # 🔁 Get related CustomWorker
        except CustomAdmin.DoesNotExist:
            return Response({"detail": "Admin profile not found."}, status=404)

        serializer = AdminProfileSerializer(admin)
        return Response(serializer.data)


class UpdateProfileView(APIView):
    permission_classes = [IsAdminUser]

    def patch(self, request):
        try:
            admin = CustomAdmin.objects.get(user=request.user)
        except CustomAdmin.DoesNotExist:
            return Response({"detail": "Admin profile not found."}, status=404)

        serializer = AdminUpdateSerializer(admin, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)


class PendingWorkerListView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        pending_workers = CustomWorker.objects.filter(approval_status='pending')
        serializer = CustomWorkerSerializer(pending_workers, many=True)
        return Response(serializer.data)


#class ApproveWorkerView(APIView):
#    permission_classes = [IsAdminUser]

#    def post(self, request, worker_id):
#        try:
#            worker = CustomWorker.objects.get(id=worker_id)
#            worker.approval_status = 'approved'
#            worker.save()
#            return Response({"detail": "Worker approved."})
#        except CustomWorker.DoesNotExist:
#            return Response({"error": "Worker not found"}, status=404)


class ApproveWorkerView(APIView):
    permission_classes = [IsAdminUser]

    def post(self, request, worker_id):
        worker = CustomWorker.objects.get(id=worker_id)
        action = request.data.get("action")

        if action == "approve":
            worker.is_verified = True
            worker.approval_status = 'approved'
            worker.verification_status = "approved"
            worker.rejection_reason = None
        elif action == "reject":
            worker.verification_status = "rejected"
            worker.rejection_reason = request.data.get("reason", "Not specified")
        else:
            return Response({"error": "Invalid action."}, status=400)

        print("after approve worker")
        print("worker.is_verified: "+str(worker.is_verified))
        print("worker.is_verified: " + str(worker.approval_status))
        print("worker.is_verified: " + str(worker.verification_status))
        worker.save()
        return Response({"message": "Worker status updated."})


class RejectWorkerView(APIView):
    permission_classes = [IsAdminUser]

    def post(self, request, worker_id):
        try:
            worker = CustomWorker.objects.get(id=worker_id)
            worker.approval_status = 'rejected'
            worker.verification_status = "rejected"
            worker.rejection_reason = request.data.get("reason", "Not specified")
            print("after reject worker")
            print("worker.is_verified: " + str(worker.is_verified))
            print("worker.is_verified: " + str(worker.approval_status))
            print("worker.is_verified: " + str(worker.verification_status))
            worker.save()
            return Response({"detail": "Worker rejected."})
        except CustomWorker.DoesNotExist:
            return Response({"error": "Worker not found"}, status=404)


class WorkerHistoryView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        workers = CustomWorker.objects.exclude(approval_status='pending')
        serializer = CustomWorkerSerializer(workers, many=True)
        return Response(serializer.data)
