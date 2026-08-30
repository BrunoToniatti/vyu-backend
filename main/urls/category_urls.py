from django.urls import path
from main.views.category_views import (
    CategoryListCreateView, CategoryDetailView,
    CategoryItemListCreateView, CategoryItemDetailView,
    UserPreferencesView, RestaurantCategoryItemsView,
)

urlpatterns = [
    # Público / Admin
    path('', CategoryListCreateView.as_view()),
    path('<int:pk>/', CategoryDetailView.as_view()),
    path('<int:category_pk>/items/', CategoryItemListCreateView.as_view()),
    path('<int:category_pk>/items/<int:pk>/', CategoryItemDetailView.as_view()),
]
