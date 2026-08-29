from django.urls import path
from main.views.user_app_views import (
    UserAppRegistrationView,
    UserAppProfileView,
)

urlpatterns = [
    path('', UserAppRegistrationView.as_view(), name='user-app-register'),
    path('me/', UserAppProfileView.as_view(), name='user-app-profile'),
]
