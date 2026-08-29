from rest_framework import serializers
from main.models.queue import Queue


class QueueSerializer(serializers.ModelSerializer):
    restaurant_name = serializers.CharField(source='restaurant.name', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = Queue
        fields = (
            'id',
            'restaurant',
            'restaurant_name',
            'status',
            'status_display',
            'current_size',
            'estimated_wait_minutes',
            'notes',
            'created_at',
            'updated_at',
        )
        read_only_fields = ('id', 'restaurant', 'restaurant_name', 'created_at', 'updated_at')


class QueueUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Queue
        fields = ('status', 'current_size', 'estimated_wait_minutes', 'notes')
