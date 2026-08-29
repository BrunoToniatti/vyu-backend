from django.urls import path
from main.views.auth_views import (
    ManagerLoginView,
    UserAppLoginView,
    TokenRefreshView,
)

urlpatterns = [
    path('manager/login/', ManagerLoginView.as_view(), name='manager-login'),
    path('app/login/', UserAppLoginView.as_view(), name='app-user-login'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token-refresh'),
]
