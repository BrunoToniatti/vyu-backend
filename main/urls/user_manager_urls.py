from django.urls import path
from main.views.user_manager_views import (
    ManagerRegistrationView,
    ManagerProfileView,
    AdminManagerListCreateView,
    AdminManagerDetailView,
)

urlpatterns = [
    path('', ManagerRegistrationView.as_view(), name='manager-register'),
    path('me/', ManagerProfileView.as_view(), name='manager-profile'),
    path('admin/', AdminManagerListCreateView.as_view(), name='admin-manager-list'),
    path('admin/<int:pk>/', AdminManagerDetailView.as_view(), name='admin-manager-detail'),
]
