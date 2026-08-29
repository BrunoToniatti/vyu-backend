from rest_framework import serializers
from main.models.bug_report import BugReport


class BugReportCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = BugReport
        fields = ('title', 'description', 'platform', 'category')


class BugReportResponseSerializer(serializers.ModelSerializer):
    opened_by_name = serializers.SerializerMethodField()
    resolved_by_name = serializers.SerializerMethodField()
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    platform_display = serializers.CharField(source='get_platform_display', read_only=True)
    category_display = serializers.CharField(source='get_category_display', read_only=True)

    class Meta:
        model = BugReport
        fields = (
            'id',
            'title',
            'description',
            'platform',
            'platform_display',
            'category',
            'category_display',
            'status',
            'status_display',
            'admin_response',
            'opened_by',
            'opened_by_name',
            'resolved_by',
            'resolved_by_name',
            'created_at',
            'updated_at',
        )
        read_only_fields = fields

    def get_opened_by_name(self, obj):
        return f"{obj.opened_by.first_name} {obj.opened_by.last_name}"

    def get_resolved_by_name(self, obj):
        if obj.resolved_by:
            return f"{obj.resolved_by.first_name} {obj.resolved_by.last_name}"
        return None


class BugReportAdminUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = BugReport
        fields = ('status', 'admin_response')
