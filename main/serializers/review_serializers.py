from rest_framework import serializers
from main.models.review import Review


class ReviewCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = ('stars', 'comment')

    def validate_stars(self, value):
        if not (1 <= value <= 5):
            raise serializers.ValidationError("Estrelas deve ser entre 1 e 5.")
        return value


class ReviewResponseSerializer(serializers.ModelSerializer):
    user_name = serializers.SerializerMethodField()
    user_photo_url = serializers.SerializerMethodField()
    user_id = serializers.SerializerMethodField()
    user_email = serializers.SerializerMethodField()
    user_phone = serializers.SerializerMethodField()
    user_preferences = serializers.SerializerMethodField()

    class Meta:
        model = Review
        fields = (
            'id', 'user_id', 'user_name', 'user_photo_url',
            'user_email', 'user_phone', 'user_preferences',
            'stars', 'comment', 'manager_response', 'created_at',
        )
        read_only_fields = fields

    def get_user_name(self, obj):
        return f"{obj.user_app.first_name} {obj.user_app.last_name}"

    def get_user_photo_url(self, obj):
        return obj.user_app.photo_url or None

    def get_user_id(self, obj):
        return obj.user_app.id

    def get_user_email(self, obj):
        return obj.user_app.email

    def get_user_phone(self, obj):
        return obj.user_app.phone_number

    def get_user_preferences(self, obj):
        return [
            {'id': item.id, 'name': item.name, 'category': item.category.name if hasattr(item, 'category') else ''}
            for item in obj.user_app.preferences.select_related('category').all()
        ]


class ManagerResponseSerializer(serializers.Serializer):
    response = serializers.CharField(max_length=1000)
