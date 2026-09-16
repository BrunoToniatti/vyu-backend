from django.urls import path
from main.views.reservation_views import (
    UserPhoneSearchView,
    ManagerReservationListCreateView,
    ManagerReservationDetailView,
)

urlpatterns = [
    path('user-search/', UserPhoneSearchView.as_view(), name='reservation-user-search'),
]
