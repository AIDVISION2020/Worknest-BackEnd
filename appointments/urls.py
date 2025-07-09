# urls.py

from django.urls import path
from .views import *

urlpatterns = [
    path('my-tickets/', MyTicketsView.as_view()),
    path('book-appointment/', BookAppointmentView.as_view()),
    path('worker/tickets/', WorkerTicketsView.as_view()),
    path('worker/ticket/<int:pk>/<str:action>/', UpdateTicketStatusView.as_view()),
    path('ticket/<int:pk>/complete-work/', CompleteWorkView.as_view()),
    path("ticket/<int:ticket_id>/confirm-completion/", ConfirmCompletionView.as_view()),
    path('ticket/<int:pk>/pay/', MarkAsPaidView.as_view()),
    #path('ticket/<int:pk>/review/', MarkAsReviewedView.as_view()),
    path("ticket/<int:ticket_id>/complete-work/", CompleteWorkView.as_view()),
    path("ticket/<int:ticket_id>/pay/", PayForTicketView.as_view()),
    path("ticket/<int:ticket_id>/submit-review/", SubmitReviewView.as_view()),
]
