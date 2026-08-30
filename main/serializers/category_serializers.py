from rest_framework import serializers
from main.models import Category, CategoryItem


class CategoryItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = CategoryItem
        fields = ['id', 'name', 'is_active']


class CategorySerializer(serializers.ModelSerializer):
    items = CategoryItemSerializer(many=True, read_only=True)

    class Meta:
        model = Category
        fields = ['id', 'name', 'description', 'is_active', 'items']


class CategoryItemCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = CategoryItem
        fields = ['id', 'category', 'name', 'is_active']


class CategoryCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'description', 'is_active']


class UserPreferencesSerializer(serializers.Serializer):
    preference_ids = serializers.ListField(
        child=serializers.IntegerField(),
        help_text="Lista de IDs de CategoryItem"
    )


class RestaurantCategoryItemsSerializer(serializers.Serializer):
    category_item_ids = serializers.ListField(
        child=serializers.IntegerField(),
        help_text="Lista de IDs de CategoryItem"
    )
