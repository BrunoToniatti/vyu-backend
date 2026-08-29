from main.models.bug_report import BugReport
from main.models.user_manager import UserManager


class BugReportService:

    @staticmethod
    def create_report(manager: UserManager, validated_data: dict) -> BugReport:
        return BugReport.objects.create(opened_by=manager, **validated_data)

    @staticmethod
    def get_all_reports():
        return BugReport.objects.select_related('opened_by', 'resolved_by').all()

    @staticmethod
    def get_manager_reports(manager: UserManager):
        return BugReport.objects.filter(opened_by=manager).select_related('opened_by', 'resolved_by')

    @staticmethod
    def update_report(report: BugReport, admin: UserManager, validated_data: dict) -> BugReport:
        for field, value in validated_data.items():
            setattr(report, field, value)
        if validated_data.get('status') in [BugReport.Status.RESOLVED, BugReport.Status.CLOSED]:
            report.resolved_by = admin
        report.save()
        return report
