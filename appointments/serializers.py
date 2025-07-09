# serializers.py

from rest_framework import serializers
from .models import AppointmentTicket, Review


class AppointmentTicketSerializer(serializers.ModelSerializer):
    class Meta:
        model = AppointmentTicket
        fields = '__all__'
        read_only_fields = ['status', 'user', 'created_at', 'updated_at', 'message', 'scheduled_date', 'location']


class ReviewSerializer(serializers.ModelSerializer):
    user_username = serializers.CharField(source="user.username", read_only=True)

    class Meta:
        model = Review
        fields = ['rating', 'comment', 'created_at', 'user_username']
