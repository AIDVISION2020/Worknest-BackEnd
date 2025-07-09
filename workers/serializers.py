from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import serializers
from rest_framework.views import APIView

from appointments.permissions import IsWorker
from users.models import CustomUser
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from workers.models import CustomWorker
from rest_framework.exceptions import AuthenticationFailed


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'password', 'role')  # role will be set automatically

    def create(self, validated_data):
        worker_user = CustomUser.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
            role='worker',  # ensure passed from view
        )
        CustomWorker.objects.create(
            user=worker_user,
            bio='Experienced and reliable.',
            approval_status='pending'
        )

        return worker_user


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['username'] = user.username
        token['role'] = user.role
        return token

    def validate(self, attrs):
        data = super().validate(attrs)
        if self.user.role == 'worker':
            try:
                worker_profile = self.user.worker_profile  # one-to-one reverse accessor
                #if worker_profile.approval_status == 'rejected':
                #    raise AuthenticationFailed("Your account was rejected by admin.")

                #if worker_profile.approval_status != 'approved':
                #    raise AuthenticationFailed("Your account is pending admin approval.")
                if not worker_profile.is_verified:
                    data['redirect'] = '/verification'
                else:
                    data['redirect'] = '/dashboard'
            except CustomWorker.DoesNotExist:
                raise AuthenticationFailed("Worker profile not found.")

        # If passed, return token data
        data['username'] = self.user.username
        data['role'] = self.user.role
        return data


class WorkerProfileSerializer(serializers.ModelSerializer):
    # Fetch from CustomUser via the `user` OneToOneField
    user_id = serializers.IntegerField(source='user.id', read_only=True)
    username = serializers.CharField(source='user.username', read_only=True)
    email = serializers.EmailField(source='user.email', read_only=True)
    phone = serializers.CharField(source='user.phone')
    gender = serializers.CharField(source='user.gender')
    dob = serializers.DateField(source='user.dob')
    location = serializers.CharField(source='user.location')
    profile_pic = serializers.ImageField(source='user.profile_pic')
    role = serializers.CharField(source='user.role', read_only=True)
    latitude = serializers.FloatField(source='user.latitude')
    longitude = serializers.FloatField(source='user.longitude')
    pincode = serializers.CharField(source='user.pincode')

    # Add any CustomWorker-specific fields here
    id = serializers.IntegerField()
    profession = serializers.CharField()
    experience_years = serializers.IntegerField(default=0)
    hourly_rate = serializers.DecimalField(max_digits=10, decimal_places=2)
    is_verified = serializers.BooleanField(default=False)
    approval_status = serializers.CharField()
    bio = serializers.CharField()

    class Meta:
        model = CustomWorker
        fields = [
            'id', 'user_id', 'username', 'email', 'phone', 'gender', 'dob',
            'location', 'profile_pic', 'role',
            'profession', 'experience_years', 'hourly_rate', 'bio', 'latitude', 'longitude', 'pincode',
            'is_verified', 'approval_status'
        ]


class WorkerUpdateSerializer(serializers.ModelSerializer):
    # CustomUser fields (editable)
    phone = serializers.CharField(source='user.phone', required=False)
    gender = serializers.CharField(source='user.gender', required=False)
    location = serializers.CharField(source='user.location', required=False)
    dob = serializers.DateField(source='user.dob', required=False)
    profile_pic = serializers.ImageField(source='user.profile_pic', required=False)
    latitude = serializers.CharField(source='user.latitude')
    longitude = serializers.CharField(source='user.longitude')
    pincode = serializers.CharField(source='user.pincode', required=False)

    # CustomWorker fields (editable)
    profession = serializers.CharField(required=False)
    experience_years = serializers.IntegerField(required=False)
    hourly_rate = serializers.DecimalField(max_digits=10, decimal_places=2, required=False)
    bio = serializers.CharField(required=False)

    class Meta:
        model = CustomWorker
        fields = [
            'phone', 'gender', 'location', 'dob', 'profile_pic',
            'profession', 'experience_years', 'hourly_rate', 'bio', 'latitude', 'longitude', 'pincode'
        ]
        read_only_fields = ['email', 'username']

    def update(self, instance, validated_data):
        # Extract nested user data
        user_data = validated_data.pop('user', {})

        # Update CustomUser fields from user_data
        for attr, value in user_data.items():
            setattr(instance.user, attr, value)
        instance.user.save()

        # Update CustomWorker-specific fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        return instance


class WorkerVerificationUploadView(APIView):
    permission_classes = [IsAuthenticated, IsWorker]

    def post(self, request):
        worker = request.user

        file = request.FILES.get('document')
        if not file or not file.name.endswith('.pdf'):
            return Response({"error": "Only PDF files allowed."}, status=400)

        worker.verification_document = file
        worker.verification_status = "pending"
        worker.save()

        return Response({"message": "Document uploaded. Please wait for approval."})
