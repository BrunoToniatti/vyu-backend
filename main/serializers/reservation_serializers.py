from rest_framework import serializers
from main.models.reservation import Reservation


class ReservationSerializer(serializers.ModelSerializer):
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    user_name = serializers.SerializerMethodField()

    class Meta:
        model = Reservation
        fields = (
            'id',
            'restaurant',
            'user_app',
            'user_name',
            'guest_name',
            'guest_phone',
            'guest_email',
            'date',
            'time',
            'party_size',
            'notes',
            'status',
            'status_display',
            'created_at',
            'updated_at',
        )
        read_only_fields = ('id', 'restaurant', 'user_app', 'user_name', 'status_display', 'created_at', 'updated_at')

    def get_user_name(self, obj):
        if obj.user_app:
            return f"{obj.user_app.first_name} {obj.user_app.last_name}".strip()
        return None


class ReservationCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reservation
        fields = ('guest_name', 'guest_phone', 'guest_email', 'date', 'time', 'party_size', 'notes')


class ReservationStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reservation
        fields = ('status',)
