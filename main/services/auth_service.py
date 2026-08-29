from django.utils import timezone
from rest_framework_simplejwt.tokens import RefreshToken
from main.models.user_manager import UserManager
from main.models.user_app import UserApp


class AuthService:
    """
    Business logic for authenticating users and issuing JWT tokens
    using djangorestframework-simplejwt with secure claims.
    """

    @staticmethod
    def _generate_tokens_for_user(user, user_type: str) -> dict:
        """
        Generates SimpleJWT access & refresh tokens with custom claims.
        """
        refresh = RefreshToken()
        # Set custom verified claims
        refresh['user_id'] = user.id
        refresh['user_type'] = user_type
        refresh['username'] = user.username
        refresh['email'] = user.email

        return {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'user_type': user_type,
        }

    @classmethod
    def authenticate_manager(cls, identifier: str, raw_password: str):
        """
        Authenticates a UserManager via email or username.
        Updates last_login and returns tokens upon success.
        Returns None on any mismatch to prevent user enumeration.
        """
        normalized_ident = identifier.strip().lower()

        manager = UserManager.objects.filter(
            email=normalized_ident
        ).first() or UserManager.objects.filter(
            username=normalized_ident
        ).first()

        if not manager or not manager.is_active:
            return None

        if not manager.check_password(raw_password):
            return None

        # Update last_login timestamp
        manager.last_login = timezone.now()
        manager.save(update_fields=['last_login', 'updated_at'])

        token_data = cls._generate_tokens_for_user(manager, "MANAGER")
        token_data['user'] = manager
        return token_data

    @classmethod
    def authenticate_user_app(cls, identifier: str, raw_password: str):
        """
        Authenticates a UserApp (Customer) via email or username.
        Updates last_login and returns tokens upon success.
        Returns None on any mismatch to prevent user enumeration.
        """
        normalized_ident = identifier.strip().lower()

        user_app = UserApp.objects.filter(
            email=normalized_ident
        ).first() or UserApp.objects.filter(
            username=normalized_ident
        ).first()

        if not user_app or not user_app.is_active:
            return None

        if not user_app.check_password(raw_password):
            return None

        # Update last_login timestamp
        user_app.last_login = timezone.now()
        user_app.save(update_fields=['last_login', 'updated_at'])

        token_data = cls._generate_tokens_for_user(user_app, "APP_USER")
        token_data['user'] = user_app
        return token_data

    @staticmethod
    def refresh_access_token(refresh_token_str: str) -> dict:
        """
        Refreshes the access token using SimpleJWT RefreshToken.
        """
        refresh = RefreshToken(refresh_token_str)
        return {
            'access': str(refresh.access_token),
        }
