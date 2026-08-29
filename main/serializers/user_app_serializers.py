import re
from rest_framework import serializers
from main.models.user_app import UserApp


class UserAppCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating a new UserApp (Mobile App consumer).
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
        model = UserApp
        fields = (
            'id',
            'first_name',
            'last_name',
            'phone_number',
            'path_photo',
            'email',
            'username',
            'password',
            'created_at',
            'updated_at',
        )
        read_only_fields = ('id', 'created_at', 'updated_at')

    def validate_email(self, value):
        normalized_email = value.strip().lower()
        if UserApp.objects.filter(email=normalized_email).exists():
            raise serializers.ValidationError("Este e-mail já está em uso por outro usuário.")
        return normalized_email

    def validate_username(self, value):
        normalized_username = value.strip().lower()
        if not re.match(r'^[a-zA-Z0-9_.-]+$', normalized_username):
            raise serializers.ValidationError("Nome de usuário contém caracteres inválidos. Use apenas letras, números e . _ -")
        if UserApp.objects.filter(username=normalized_username).exists():
            raise serializers.ValidationError("Este nome de usuário já está em uso.")
        return normalized_username

    def validate_phone_number(self, value):
        cleaned_phone = re.sub(r'\D', '', value)
        if len(cleaned_phone) < 10 or len(cleaned_phone) > 15:
            raise serializers.ValidationError("Número de telefone inválido.")
        return value.strip()


class UserAppResponseSerializer(serializers.ModelSerializer):
    """
    Serializer for returning UserApp details.
    CRITICAL: Never includes password, password_hash or sensitive internal credentials.
    """
    class Meta:
        model = UserApp
        fields = (
            'id',
            'first_name',
            'last_name',
            'phone_number',
            'path_photo',
            'email',
            'username',
            'last_login',
            'created_at',
            'updated_at',
        )
        read_only_fields = fields


class UserAppUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for updating UserApp profile.
    Prevents modification of id, email, username, password, or timestamps through this endpoint.
    """
    class Meta:
        model = UserApp
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
