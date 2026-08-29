import re
from rest_framework import serializers
from main.models.restaurant import Restaurant


class RestaurantCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating a new Restaurant.
    Strictly protects manager association: manager is populated
    exclusively from request.user in the service layer, preventing mass assignment.
    """
    class Meta:
        model = Restaurant
        fields = (
            'id',
            'cnpj',
            'contact_phone',
            'name',
            'address',
            'site',
            'instagram',
            'path_logo',
            'created_at',
            'updated_at',
        )
        read_only_fields = ('id', 'created_at', 'updated_at')

    def validate_name(self, value):
        if not value or not value.strip():
            raise serializers.ValidationError("O nome do restaurante é obrigatório.")
        return value.strip()

    def validate_address(self, value):
        if not value or not value.strip():
            raise serializers.ValidationError("O endereço do restaurante é obrigatório.")
        return value.strip()

    def validate_cnpj(self, value):
        cleaned_cnpj = re.sub(r'\D', '', value)
        if len(cleaned_cnpj) != 14:
            raise serializers.ValidationError("CNPJ deve conter exatamente 14 dígitos numéricos.")
        return value.strip()

    def validate_contact_phone(self, value):
        cleaned_phone = re.sub(r'\D', '', value)
        if len(cleaned_phone) < 10 or len(cleaned_phone) > 15:
            raise serializers.ValidationError("Número de telefone de contato inválido.")
        return value.strip()


class RestaurantUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for updating an existing Restaurant.
    Guards against mass assignment: id, manager, created_at, updated_at cannot be altered.
    """
    class Meta:
        model = Restaurant
        fields = (
            'cnpj',
            'contact_phone',
            'name',
            'address',
            'site',
            'instagram',
            'path_logo',
        )

    def validate_name(self, value):
        if value is not None and not value.strip():
            raise serializers.ValidationError("O nome do restaurante não pode ser vazio.")
        return value.strip() if value else value

    def validate_address(self, value):
        if value is not None and not value.strip():
            raise serializers.ValidationError("O endereço do restaurante não pode ser vazio.")
        return value.strip() if value else value

    def validate_cnpj(self, value):
        if value:
            cleaned_cnpj = re.sub(r'\D', '', value)
            if len(cleaned_cnpj) != 14:
                raise serializers.ValidationError("CNPJ deve conter exatamente 14 dígitos numéricos.")
            return value.strip()
        return value

    def validate_contact_phone(self, value):
        if value:
            cleaned_phone = re.sub(r'\D', '', value)
            if len(cleaned_phone) < 10 or len(cleaned_phone) > 15:
                raise serializers.ValidationError("Número de telefone de contato inválido.")
            return value.strip()
        return value


class RestaurantAdminResponseSerializer(serializers.ModelSerializer):
    """
    Administrative serializer for the owning manager.
    Returns complete restaurant information including manager_id and timestamps.
    """
    manager_id = serializers.IntegerField(source='manager.id', read_only=True)

    class Meta:
        model = Restaurant
        fields = (
            'id',
            'cnpj',
            'manager_id',
            'name',
            'address',
            'contact_phone',
            'site',
            'instagram',
            'path_logo',
            'created_at',
            'updated_at',
        )
        read_only_fields = fields


class RestaurantTransferSerializer(serializers.Serializer):
    """
    Admin-only serializer for transferring restaurant ownership to another manager.
    """
    new_manager_id = serializers.IntegerField()


class RestaurantPublicResponseSerializer(serializers.ModelSerializer):
    """
    Public serializer for Mobile App consumers and anonymous visitors.
    CRITICAL: Never exposes manager_id, manager credentials, or administrative details.
    """
    class Meta:
        model = Restaurant
        fields = (
            'id',
            'name',
            'address',
            'contact_phone',
            'site',
            'instagram',
            'path_logo',
        )
        read_only_fields = fields
