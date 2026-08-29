from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import NotFound

from main.permissions import IsAdmin, IsManager
from main.serializers.bug_report_serializers import (
    BugReportCreateSerializer,
    BugReportResponseSerializer,
    BugReportAdminUpdateSerializer,
)
from main.services.bug_report_service import BugReportService
from main.models.bug_report import BugReport


class ManagerBugReportListCreateView(APIView):
    """
    Manager: list own reports or open a new one.
    """
    permission_classes = [IsManager]

    def get(self, request):
        reports = BugReportService.get_manager_reports(request.user)
        serializer = BugReportResponseSerializer(reports, many=True)
        return Response({"status": "success", "status_code": 200, "count": reports.count(), "data": serializer.data})

    def post(self, request):
        serializer = BugReportCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        report = BugReportService.create_report(request.user, serializer.validated_data)
        return Response(
            {"status": "success", "status_code": 201, "data": BugReportResponseSerializer(report).data},
            status=status.HTTP_201_CREATED
        )


class AdminBugReportListView(APIView):
    """
    Admin: list all reports from all managers.
    """
    permission_classes = [IsAdmin]

    def get(self, request):
        reports = BugReportService.get_all_reports()
        serializer = BugReportResponseSerializer(reports, many=True)
        return Response({"status": "success", "status_code": 200, "count": reports.count(), "data": serializer.data})


class AdminBugReportDetailView(APIView):
    """
    Admin: respond to or update a specific report.
    """
    permission_classes = [IsAdmin]

    def get(self, request, pk):
        try:
            report = BugReport.objects.select_related('opened_by', 'resolved_by').get(pk=pk)
        except BugReport.DoesNotExist:
            raise NotFound("Chamado não encontrado.")
        return Response({"status": "success", "status_code": 200, "data": BugReportResponseSerializer(report).data})

    def put(self, request, pk):
        try:
            report = BugReport.objects.get(pk=pk)
        except BugReport.DoesNotExist:
            raise NotFound("Chamado não encontrado.")
        serializer = BugReportAdminUpdateSerializer(data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        report = BugReportService.update_report(report, request.user, serializer.validated_data)
        return Response({"status": "success", "status_code": 200, "data": BugReportResponseSerializer(report).data})
