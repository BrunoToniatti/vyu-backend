from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken, AuthenticationFailed
from main.models.user_manager import UserManager
from main.models.user_app import UserApp


class CustomJWTAuthentication(JWTAuthentication):
    """
    Custom JWT Authentication using djangorestframework-simplejwt.
    Resolves the authenticated model instance (UserManager or UserApp)
    based strictly on verified token claims (user_id, user_type).
    """

    def authenticate(self, request):
        try:
            return super().authenticate(request)
        except Exception:
            return None

    def get_user(self, validated_token):
        """
        Attempts to find and return a user using the given validated token.
        Never trusts client-supplied query parameters or headers.
        """
        try:
            user_id = validated_token.get('user_id')
            user_type = validated_token.get('user_type')
        except KeyError:
            raise InvalidToken("Token não contém identificadores válidos.")

        if not user_id or not user_type:
            raise InvalidToken("Claims de identidade ausentes no token.")

        if user_type == "MANAGER":
            try:
                user = UserManager.objects.get(id=user_id, is_active=True)
                return user
            except UserManager.DoesNotExist:
                raise AuthenticationFailed("Gerente não encontrado ou inativo.", code="user_not_found")

        elif user_type == "APP_USER":
            try:
                user = UserApp.objects.get(id=user_id, is_active=True)
                return user
            except UserApp.DoesNotExist:
                raise AuthenticationFailed("Usuário do aplicativo não encontrado ou inativo.", code="user_not_found")

        else:
            raise InvalidToken("Tipo de usuário inválido no token.")
