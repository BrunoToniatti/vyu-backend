from django.urls import path
from main.views.user_manager_views import (
    ManagerRegistrationView,
    ManagerProfileView,
)

urlpatterns = [
    path('', ManagerRegistrationView.as_view(), name='manager-register'),
    path('me/', ManagerProfileView.as_view(), name='manager-profile'),
]
