from main.views.auth_views import (
    ManagerLoginView,
    UserAppLoginView,
    TokenRefreshView,
)
from main.views.user_manager_views import (
    ManagerRegistrationView,
    ManagerProfileView,
)
from main.views.user_app_views import (
    UserAppRegistrationView,
    UserAppProfileView,
)
from main.views.restaurant_views import (
    ManagerRestaurantListCreateView,
    ManagerRestaurantDetailView,
    PublicRestaurantListView,
    PublicRestaurantDetailView,
)

__all__ = [
    'ManagerLoginView',
    'UserAppLoginView',
    'TokenRefreshView',
    'ManagerRegistrationView',
    'ManagerProfileView',
    'UserAppRegistrationView',
    'UserAppProfileView',
    'ManagerRestaurantListCreateView',
    'ManagerRestaurantDetailView',
    'PublicRestaurantListView',
    'PublicRestaurantDetailView',
]
