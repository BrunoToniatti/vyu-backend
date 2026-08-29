import re
from rest_framework import serializers
from main.models.user_manager import UserManager


class UserManagerCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating a new UserManager (Manager Web user).
    Protects sensitive fields and enforces validation.
    """
    password = serializers.CharField(
        write_only=True,
        required=True,
        min_length=8,
        style={'input_type': 'password'},
        help_text="Senha com no mínimo 8 caracteres."
    )

    class Meta:
        model = UserManager
        fields = (
            'id',
            'first_name',
            'last_name',
            'phone_number',
            'path_photo',
            'email',
            'username',
            'password',
            'restaurant_count',
            'created_at',
            'updated_at',
        )
        read_only_fields = ('id', 'restaurant_count', 'created_at', 'updated_at')

    def validate_email(self, value):
        normalized_email = value.strip().lower()
        if UserManager.objects.filter(email=normalized_email).exists():
            raise serializers.ValidationError("Este e-mail já está em uso por outro gerente.")
        return normalized_email

    def validate_username(self, value):
        normalized_username = value.strip().lower()
        if not re.match(r'^[a-zA-Z0-9_.-]+$', normalized_username):
            raise serializers.ValidationError("Nome de usuário contém caracteres inválidos. Use apenas letras, números e . _ -")
        if UserManager.objects.filter(username=normalized_username).exists():
            raise serializers.ValidationError("Este nome de usuário já está em uso.")
        return normalized_username

    def validate_phone_number(self, value):
        cleaned_phone = re.sub(r'\D', '', value)
        if len(cleaned_phone) < 10 or len(cleaned_phone) > 15:
            raise serializers.ValidationError("Número de telefone inválido.")
        return value.strip()


class UserManagerResponseSerializer(serializers.ModelSerializer):
    """
    Serializer for returning UserManager details.
    CRITICAL: Never includes password, password_hash or sensitive internal credentials.
    """
    restaurant_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = UserManager
        fields = (
            'id',
            'first_name',
            'last_name',
            'phone_number',
            'path_photo',
            'email',
            'username',
            'is_admin',
            'restaurant_count',
            'last_login',
            'created_at',
            'updated_at',
        )
        read_only_fields = fields


class UserManagerUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for updating UserManager profile.
    Prevents modification of id, email, username, password, or timestamps through this endpoint.
    """
    class Meta:
        model = UserManager
        fields = (
            'first_name',
            'last_name',
            'phone_number',
            'path_photo',
        )

    def validate_phone_number(self, value):
        if value:
            cleaned_phone = re.sub(r'\D', '', value)
            if len(cleaned_phone) < 10 or len(cleaned_phone) > 15:
                raise serializers.ValidationError("Número de telefone inválido.")
            return value.strip()
        return value
