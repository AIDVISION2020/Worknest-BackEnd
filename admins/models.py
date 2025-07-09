#from django.contrib.auth.models import AbstractUser
from django.db import models
from worknest import settings


class CustomAdmin(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='admin_profile')
    user.role = "admin"

    admin_code = models.CharField(max_length=20, blank=True, null=True)  # optional, can be any admin-specific field
    access_level = models.CharField(max_length=50, default="supervisor")

    def __str__(self):
        return f"{self.user.username} ({self.user.role})"
