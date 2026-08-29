from django.urls import path
from main.views.bug_report_views import (
    ManagerBugReportListCreateView,
    AdminBugReportListView,
    AdminBugReportDetailView,
)

urlpatterns = [
    path('', ManagerBugReportListCreateView.as_view(), name='manager-bug-report-list-create'),
    path('admin/', AdminBugReportListView.as_view(), name='admin-bug-report-list'),
    path('admin/<int:pk>/', AdminBugReportDetailView.as_view(), name='admin-bug-report-detail'),
]
