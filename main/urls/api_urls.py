from django.urls import path, include
from main.views.category_views import UserPreferencesView, RestaurantCategoryItemsView

urlpatterns = [
    # AUTH
    path('auth/', include('main.urls.auth_urls')),

    # USER_MANAGER
    path('managers/', include('main.urls.user_manager_urls')),

    # USER_APP
    path('users/', include('main.urls.user_app_urls')),

    # RESTAURANT
    path('restaurants/', include('main.urls.restaurant_urls')),

    # QUEUE
    path('queues/', include('main.urls.queue_urls')),

    # RESERVATIONS
    path('reservations/', include('main.urls.reservation_urls')),

    # BUG REPORTS
    path('reports/', include('main.urls.bug_report_urls')),

    # CATEGORIES
    path('categories/', include('main.urls.category_urls')),

    # USER PREFERENCES
    path('users/me/preferences/', UserPreferencesView.as_view()),

    # RESTAURANT CATEGORIES
    path('restaurants/<int:restaurant_pk>/categories/', RestaurantCategoryItemsView.as_view()),
]
