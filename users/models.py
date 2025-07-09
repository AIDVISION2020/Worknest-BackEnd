from django.contrib.auth.models import AbstractUser, PermissionsMixin
from django.db import models
from django.core.validators import RegexValidator


class CustomUser(AbstractUser, PermissionsMixin):
    username = models.CharField(max_length=150, unique=True)
    email = models.EmailField(unique=True)
    ROLE_CHOICES = (
        ('user', 'User'),
        ('worker', 'Worker'),
        ('admin', 'Admin'),
    )
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='user')
    gender = models.CharField(max_length=10, blank=True, null=True)
    dob = models.DateField(blank=True, null=True)
    latitude = models.CharField(max_length=25, null=True, blank=True)
    longitude = models.CharField(max_length=25, null=True, blank=True)
    location = models.CharField(max_length=255, blank=True, null=True)
    pincode = models.CharField(
        max_length=6,
        validators=[RegexValidator(r'^\d{6}$', message="Enter a valid 6 digit pincode")],
        null=True,
        blank=True
    )
    phone = models.CharField(max_length=15, blank=True, null=True)
    profile_pic = models.ImageField(upload_to='profile_pics/', blank=True, null=True)

    REQUIRED_FIELDS = ['role']

    def __str__(self):
        return f"{self.username} ({self.role})"
