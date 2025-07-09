#from django.contrib.auth.models import AbstractUser
from django.db import models
from worknest import settings


class CustomWorker(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='worker_profile')
    status_choices = [
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
    ]
    approval_status = models.CharField(max_length=10, choices=status_choices, default='pending')

    is_verified = models.BooleanField(default=False)  # ✅ used to gate dashboard access
    verification_document = models.FileField(upload_to='verification_docs/', null=True, blank=True)
    verification_status = models.CharField(
        max_length=10,
        choices=[('pending', 'Pending'), ('approved', 'Approved'), ('rejected', 'Rejected')],
        default='pending'
    )
    rejection_reason = models.TextField(null=True, blank=True)

    ROLE_CHOICES = (
        ('user', 'User'),
        ('worker', 'Worker'),
        ('admin', 'Admin'),
    )

    #user.role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='worker')
    profession = models.CharField(max_length=100)
    experience_years = models.PositiveIntegerField(default=0)
    hourly_rate = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    bio = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.user.username} ({self.user.role})"

# Create your models here.
