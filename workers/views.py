from rest_framework.parsers import MultiPartParser
from rest_framework_simplejwt.views import TokenObtainPairView
from .serializers import RegisterSerializer, CustomTokenObtainPairSerializer, WorkerProfileSerializer, WorkerUpdateSerializer
from rest_framework_simplejwt.tokens import RefreshToken, TokenError
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from .models import CustomWorker
from rest_framework import generics, permissions
from worknest import settings
from rest_framework.permissions import IsAdminUser
import requests
import os


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


class WorkerRegisterView(RoleBasedRegisterView):
    role = 'worker'


class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer


class WorkerProfileMe(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            worker = CustomWorker.objects.get(user=request.user)
            serializer = WorkerProfileSerializer(worker)
            return Response(serializer.data)
        except CustomWorker.DoesNotExist:
            return Response({"error": "Worker profile not found"}, status=404)


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


class WorkerProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            worker = request.user.worker_profile  # 🔁 Get related CustomWorker
        except CustomWorker.DoesNotExist:
            return Response({"detail": "Worker profile not found."}, status=404)

        serializer = WorkerProfileSerializer(worker)
        return Response(serializer.data)


class UpdateProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request):
        try:
            worker = CustomWorker.objects.get(user=request.user)
        except CustomWorker.DoesNotExist:
            return Response({"detail": "Worker profile not found."}, status=404)

        serializer = WorkerUpdateSerializer(worker, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)


class WorkerListAPIView(generics.ListAPIView):
    serializer_class = WorkerProfileSerializer
    permission_classes = [permissions.AllowAny]  # Or use IsAuthenticated if needed

    def get_queryset(self):
        return CustomWorker.objects.select_related('user').filter(user__role='worker', approval_status='approved')


class AllWorkerListAPIView(generics.ListAPIView):
    serializer_class = WorkerProfileSerializer
    permission_classes = [permissions.AllowAny]  # Or use IsAuthenticated if needed

    def get_queryset(self):
        return CustomWorker.objects.select_related('user').filter(user__role='worker')


class ClosestWorkersByDistance(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user_lat = request.data.get('lat')
        user_lng = request.data.get('lng')

        if not (user_lat and user_lng):
            return Response({"error": "Latitude and longitude are required"}, status=400)

        # Fetch only workers who have a valid lat/lng
        workers = CustomWorker.objects.filter(
            #is_approved=True,
            #is_active=True,
            user__latitude__isnull=False,
            user__longitude__isnull=False
        ).select_related('user')

        if not workers.exists():
            return Response({"error": "No available workers with location data"}, status=404)
        #for worker in workers:
            #print(worker.user.username)
            #print(worker.user.latitude)
        # Prepare destination string for Google API
        destinations = "|".join([
            f"{worker.user.latitude},{worker.user.longitude}"
            for worker in workers
            if worker.user.latitude is not None and worker.user.longitude is not None
        ])

        GOOGLE_API_KEY = settings.GOOGLE_API_KEY
        #print("GOOGLE_API_KEY : "+str(GOOGLE_API_KEY))
        url = (
            f"https://maps.googleapis.com/maps/api/distancematrix/json"
            f"?origins={user_lat},{user_lng}"
            f"&destinations={destinations}"
            f"&key={'AIzaSyAp7HUI_JnnGyB__xo5RYKWJkobIpPE7WM'}"
        )

        response = requests.get(url)
        data = response.json()
        #print("Response JSON:", data)

        if data.get("status") != "OK":
            return Response({"error": "Failed to fetch from Google"}, status=500)

        try:
            distances = data["rows"][0]["elements"]
        except (KeyError, IndexError) as e:
            print("Distance Matrix parsing error:", str(e))
            return Response({"error": "Invalid Google Distance Matrix response"}, status=500)
        results = []

        for i, element in enumerate(distances):
            if element.get("status") == "OK":
                worker = list(workers)[i]
                results.append({
                    "worker_id": worker.id,
                    "username": worker.user.username,
                    "profession": worker.profession,
                    "experience_years": worker.experience_years,
                    "hourly_rate": worker.hourly_rate,
                    "bio": worker.bio,
                    "location": worker.user.location,
                    "distance_text": element["distance"]["text"],
                    "distance_value": element["distance"]["value"],
                    "duration_text": element["duration"]["text"],
                    "lat": worker.user.latitude,
                    "lng": worker.user.longitude,
                    "profile_pic": worker.user.profile_pic.url if worker.user.profile_pic else None,
                    "role": worker.user.role
                })

        sorted_results = sorted(results, key=lambda x: x["distance_value"])
        #print(sorted_results)
        return Response(sorted_results)


class UploadVerificationDoc(APIView):
    #print("in")
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser]
    #print("in2")
    def post(self, request, worker_id):
        worker = CustomWorker.objects.get(id=worker_id)
        #print("in3")
        if 'verification_document' not in request.data:
            #print("in4")
            return Response({"error": "No file uploaded."}, status=400)
        #print("before")
        worker.verification_document = request.FILES.get('verification_document')
        #print("after")
        worker.approval_status = "pending"
        worker.save()
        return Response({"message": "Document uploaded. Await admin approval."})