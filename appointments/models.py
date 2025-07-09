from django.db import models
from workers.models import CustomWorker
from worknest import settings


class AppointmentTicket(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="tickets")
    worker = models.ForeignKey(CustomWorker, on_delete=models.CASCADE, related_name="tickets")

    STATUS_CHOICES = [
        ("requested", "Requested"),
        ("rejected", "Rejected"),
        ("accepted", "Accepted"),
        ("in_progress", "In Progress"),
        ("completed", "Completed"),
        ("paid", "Paid"),
        ("reviewed", "Reviewed"),
    ]
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default="requested")
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    message = models.TextField(blank=True)
    scheduled_date = models.DateTimeField(null=True, blank=True)
    location = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return f"Ticket: {self.user.username} ({self.status})"


class Review(models.Model):
    ticket = models.OneToOneField(AppointmentTicket, on_delete=models.CASCADE, related_name='review')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    #worker = models.ForeignKey(CustomWorker, on_delete=models.CASCADE)
    rating = models.IntegerField()
    feedback = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    comment = models.TextField()

    def __str__(self):
        return f"Review for {self.ticket.id} - {self.rating}⭐"


class TicketStageHistory(models.Model):
    ticket = models.ForeignKey(AppointmentTicket, on_delete=models.CASCADE, related_name="history")
    status = models.CharField(max_length=50)
    timestamp = models.DateTimeField(auto_now_add=True)
    note = models.TextField(blank=True, null=True)
