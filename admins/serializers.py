from rest_framework import serializers
from users.models import CustomUser
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from workers.models import CustomWorker
from .models import CustomAdmin
from worknest import settings


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'password', 'role')  # role will be set automatically

    def create(self, validated_data):
        admin_user = CustomUser.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
            role='admin',  # ensure passed from view
            is_staff=True,
            is_superuser=True
        )
        CustomAdmin.objects.create(
            user=admin_user,
        )

        return admin_user


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['username'] = user.username
        token['role'] = user.role
        return token

    def validate(self, attrs):
        data = super().validate(attrs)
        data['username'] = self.user.username
        data['role'] = self.user.role
        return data


class AdminProfileSerializer(serializers.ModelSerializer):
    # Fetch from CustomUser via the `user` OneToOneField
    id = serializers.IntegerField(source='user.id', read_only=True)
    username = serializers.CharField(source='user.username', read_only=True)
    email = serializers.EmailField(source='user.email', read_only=True)
    phone = serializers.CharField(source='user.phone')
    gender = serializers.CharField(source='user.gender')
    dob = serializers.DateField(source='user.dob')
    location = serializers.CharField(source='user.location')
    profile_pic = serializers.ImageField(source='user.profile_pic')
    role = serializers.CharField(source='user.role', read_only=True)

    # Add any CustomAdmin-specific fields here
    admin_code = serializers.CharField()
    access_level = serializers.CharField()

    class Meta:
        model = CustomAdmin
        fields = [
            'id', 'username', 'email', 'phone', 'gender', 'dob',
            'location', 'profile_pic', 'role',
            'admin_code', 'access_level'
        ]


class AdminUpdateSerializer(serializers.ModelSerializer):
    # CustomUser fields (editable)
    phone = serializers.CharField(source='user.phone', required=False)
    gender = serializers.CharField(source='user.gender', required=False)
    location = serializers.CharField(source='user.location', required=False)
    dob = serializers.DateField(source='user.dob', required=False)
    profile_pic = serializers.ImageField(source='user.profile_pic', required=False)

    # CustomAdmin fields (editable)
    admin_code = serializers.CharField(required=False)
    access_level = serializers.CharField(required=False)

    class Meta:
        model = CustomAdmin
        fields = [
            'phone', 'gender', 'location', 'dob', 'profile_pic',
            'admin_code', 'access_level'
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


class CustomWorkerSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    email = serializers.EmailField(source='user.email', read_only=True)

    class Meta:
        model = CustomWorker
        fields = ['id', 'username', 'email', 'approval_status', 'bio', "verification_document"]
