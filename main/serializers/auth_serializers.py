from rest_framework import serializers


class LoginRequestSerializer(serializers.Serializer):
    """
    Serializer for login requests.
    Accepts identifier (email or username) and raw password.
    """
    identifier = serializers.CharField(
        required=True,
        max_length=255,
        help_text="E-mail ou nome de usuário cadastrado."
    )
    password = serializers.CharField(
        required=True,
        write_only=True,
        style={'input_type': 'password'},
        help_text="Senha em texto puro a ser verificada contra o hash do banco."
    )


class TokenRefreshRequestSerializer(serializers.Serializer):
    """
    Serializer for refreshing JWT access tokens.
    """
    refresh = serializers.CharField(required=True)
