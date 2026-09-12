from django.urls import path
from main.views.user_app_views import (
    UserAppRegistrationView,
    UserAppProfileView,
)
from main.views.photo_views import UserPhotoUploadView

urlpatterns = [
    path('', UserAppRegistrationView.as_view(), name='user-app-register'),
    path('me/', UserAppProfileView.as_view(), name='user-app-profile'),
    path('me/photo/', UserPhotoUploadView.as_view(), name='user-app-photo'),
]
