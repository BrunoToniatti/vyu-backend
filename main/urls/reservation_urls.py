from django.urls import path
from main.views.reservation_views import (
    UserPhoneSearchView,
    MyReservationsView,
)

urlpatterns = [
    path('user-search/', UserPhoneSearchView.as_view(), name='reservation-user-search'),
    path('mine/', MyReservationsView.as_view(), name='my-reservations'),
]
