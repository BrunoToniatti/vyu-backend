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

    class Meta:
        model = Review
        fields = (
            'id', 'user_name', 'stars', 'comment',
            'manager_response', 'created_at',
        )
        read_only_fields = fields

    def get_user_name(self, obj):
        return f"{obj.user_app.first_name} {obj.user_app.last_name}"


class ManagerResponseSerializer(serializers.Serializer):
    response = serializers.CharField(max_length=1000)
