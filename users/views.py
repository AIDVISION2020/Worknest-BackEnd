from rest_framework.decorators import api_view, permission_classes
from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken, TokenError

from appointments.models import AppointmentTicket
from appointments.permissions import IsUser
from appointments.serializers import AppointmentTicketSerializer
from .models import CustomUser
from .serializers import (RegisterSerializer, CustomTokenObtainPairSerializer, UserProfileSerializer,
                          UserUpdateSerializer)
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status


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


class UserRegisterView(RoleBasedRegisterView):
    role = 'user'


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


class UserProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        serializer = UserProfileSerializer(user)
        return Response(serializer.data)


class UpdateProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request):
        user = request.user
        serializer = UserUpdateSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        else:
            print("Serializer Errors:", serializer.errors)  # <-- this is 🔑
            return Response(serializer.errors, status=400)
        #return Response(serializer.errors, status=400)


class MyTicketsView(ListAPIView):
    serializer_class = AppointmentTicketSerializer
    permission_classes = [IsAuthenticated, IsUser]

    def get_queryset(self):
        return AppointmentTicket.objects.filter(user=self.request.user).order_by('-created_at')
