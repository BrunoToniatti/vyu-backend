from rest_framework import serializers
from main.models.queue import Queue


class QueueSerializer(serializers.ModelSerializer):
    restaurant_name = serializers.CharField(source='restaurant.name', read_only=True)
    status_display  = serializers.CharField(source='get_status_display', read_only=True)
    live_data_capture = serializers.BooleanField(source='restaurant.live_data_capture', read_only=True)

    # Computed fields — override stored values when live_data_capture is on
    current_tables = serializers.SerializerMethodField()
    max_tables     = serializers.SerializerMethodField()
    occupancy_pct  = serializers.SerializerMethodField()

    class Meta:
        model = Queue
        fields = (
            'id',
            'restaurant',
            'restaurant_name',
            'live_data_capture',
            'status',
            'status_display',
            'current_size',
            'max_capacity',
            'current_tables',
            'max_tables',
            'occupancy_pct',
            'estimated_wait_minutes',
            'notes',
            'created_at',
            'updated_at',
        )
        read_only_fields = ('id', 'restaurant', 'restaurant_name', 'created_at', 'updated_at')

    def _live(self, obj):
        return getattr(obj.restaurant, 'live_data_capture', False)

    def get_max_tables(self, obj):
        if self._live(obj):
            return obj.restaurant.restaurant_tables.count()
        return obj.max_tables

    def get_current_tables(self, obj):
        if self._live(obj):
            return obj.restaurant.comandas.filter(status='OPEN').count()
        return obj.current_tables

    def get_occupancy_pct(self, obj):
        max_t = self.get_max_tables(obj)
        cur_t = self.get_current_tables(obj)
        if max_t and max_t > 0:
            return round((cur_t / max_t) * 100, 1)
        return 0.0


class QueueUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Queue
        fields = ('status', 'current_size', 'max_capacity', 'current_tables', 'max_tables', 'estimated_wait_minutes', 'notes')
