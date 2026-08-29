from django.db import transaction
from rest_framework.exceptions import ValidationError
from main.models.user_app import UserApp


class UserAppService:
    """
    Business logic layer for UserApp (Customer) entity.
    """

    @classmethod
    @transaction.atomic
    def create_user_app(cls, validated_data: dict) -> UserApp:
        """
        Creates a new App User with safely hashed password.
        """
        raw_password = validated_data.pop('password', None)
        if not raw_password:
            raise ValidationError({'password': ['A senha é obrigatória.']})

        user_app = UserApp(**validated_data)
        # Apply secure PBKDF2 hashing
        user_app.set_password(raw_password)
        user_app.save()
        return user_app

    @classmethod
    @transaction.atomic
    def update_user_app(cls, user_app: UserApp, validated_data: dict) -> UserApp:
        """
        Updates allowed profile fields for an app user.
        """
        for field, value in validated_data.items():
            setattr(user_app, field, value)
        user_app.save()
        return user_app

    @classmethod
    @transaction.atomic
    def deactivate_user_app(cls, user_app: UserApp) -> None:
        """
        Soft deletes / deactivates an app user.
        """
        user_app.is_active = False
        user_app.save(update_fields=['is_active', 'updated_at'])
