from django.urls import path
from main.views.queue_views import AdminQueueListView, AdminQueueDetailView, ManagerQueueView

urlpatterns = [
    path('admin/', AdminQueueListView.as_view(), name='admin-queue-list'),
    path('admin/<int:restaurant_pk>/', AdminQueueDetailView.as_view(), name='admin-queue-detail'),
    path('restaurant/<int:restaurant_pk>/', ManagerQueueView.as_view(), name='manager-queue'),
]
