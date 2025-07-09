
from rest_framework import generics, status
from rest_framework.generics import ListAPIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import AppointmentTicket
from .serializers import AppointmentTicketSerializer, ReviewSerializer
from .permissions import IsUser, IsWorker
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from .models import Review


class MyTicketsView(APIView):
    permission_classes = [IsAuthenticated, IsUser]

    def get(self, request):
        tickets = AppointmentTicket.objects.filter(user=request.user).order_by("-created_at")
        serializer = AppointmentTicketSerializer(tickets, many=True)
        return Response(serializer.data)


class BookAppointmentView(generics.CreateAPIView):
    queryset = AppointmentTicket.objects.all()
    serializer_class = AppointmentTicketSerializer
    permission_classes = [IsAuthenticated, IsUser]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user, status='requested')


class WorkerTicketsView(generics.ListAPIView):
    serializer_class = AppointmentTicketSerializer
    permission_classes = [IsAuthenticated, IsWorker]

    def get_queryset(self):
        return AppointmentTicket.objects.filter(worker__user=self.request.user)


class UpdateTicketStatusView(APIView):
    permission_classes = [IsAuthenticated, IsWorker]

    def post(self, request, pk, action):
        try:
            ticket = AppointmentTicket.objects.get(pk=pk, worker__user=request.user)
        except AppointmentTicket.DoesNotExist:
            return Response({"error": "Ticket not found"}, status=404)

        if action == "accept":
            ticket.status = "accepted"
        elif action == "reject":
            ticket.status = "rejected"
        else:
            return Response({"error": "Invalid action"}, status=400)

        ticket.save()
        return Response({"status": ticket.status})


class CompleteWorkView(APIView):
    permission_classes = [IsAuthenticated, IsWorker]

    def post(self, request, pk):
        ticket = AppointmentTicket.objects.filter(pk=pk, worker__user=request.user).first()
        if not ticket or ticket.status != 'accepted':
            return Response({"error": "Invalid request"}, status=400)

        ticket.status = "awaiting_user_confirmation"
        ticket.save()
        return Response({"status": "awaiting_user_confirmation"})


class ConfirmCompletionView(APIView):
    permission_classes = [IsAuthenticated, IsUser]

    def post(self, request, ticket_id):
        ticket = get_object_or_404(AppointmentTicket, id=ticket_id, user=request.user)
        if ticket.status != 'awaiting_user_confirmation':
            return Response({"error": "Work has not been marked as done yet."}, status=400)
        ticket.status = 'completed'
        ticket.save()
        return Response({"status": "completed"})


class MarkAsPaidView(APIView):
    permission_classes = [IsAuthenticated, IsUser]

    def post(self, request, pk):
        ticket = AppointmentTicket.objects.filter(pk=pk, user=request.user).first()
        if not ticket or ticket.status != 'completed':
            return Response({"error": "Invalid request"}, status=400)

        ticket.status = "paid"
        ticket.save()
        return Response({"status": "paid"})


class PayForTicketView(APIView):
    permission_classes = [IsAuthenticated, IsUser]

    def post(self, request, ticket_id):
        ticket = get_object_or_404(AppointmentTicket, id=ticket_id, user=request.user)
        if ticket.status != 'completed':
            return Response({"error": "Cannot pay yet."}, status=400)
        ticket.status = 'paid'
        ticket.save()
        return Response({"status": "paid"})


class SubmitReviewView(APIView):
    permission_classes = [IsAuthenticated, IsUser]
    def post(self, request, ticket_id):
        ticket = AppointmentTicket.objects.filter(id=ticket_id, user=request.user).first()

        if not ticket:
            return Response({"error": "Ticket not found."}, status=404)

        if ticket.status != "paid":
            return Response({"error": "Cannot review. Payment not done."}, status=400)

        if hasattr(ticket, "review"):
            return Response({"error": "Review already submitted."}, status=400)

        serializer = ReviewSerializer(data=request.data)
        if serializer.is_valid():
            Review.objects.create(
                ticket=ticket,
                user=request.user,
                #worker=ticket.worker,
                rating=serializer.validated_data["rating"],
                comment=serializer.validated_data["comment"]
            )
            ticket.status = "reviewed"
            ticket.save()
            return Response({"message": "Review submitted!"}, status=201)

        return Response(serializer.errors, status=400)
