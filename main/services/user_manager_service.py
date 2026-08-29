from django.db import transaction
from rest_framework.exceptions import ValidationError
from main.models.user_manager import UserManager


class UserManagerService:
    """
    Business logic layer for UserManager entity.
    """

    @classmethod
    @transaction.atomic
    def create_manager(cls, validated_data: dict) -> UserManager:
        """
        Creates a new Manager with safely hashed password.
        """
        raw_password = validated_data.pop('password', None)
        if not raw_password:
            raise ValidationError({'password': ['A senha é obrigatória.']})

        manager = UserManager(**validated_data)
        # Apply secure PBKDF2 hashing
        manager.set_password(raw_password)
        manager.save()
        return manager

    @classmethod
    @transaction.atomic
    def update_manager(cls, manager: UserManager, validated_data: dict) -> UserManager:
        """
        Updates allowed profile fields for a manager.
        """
        for field, value in validated_data.items():
            setattr(manager, field, value)
        manager.save()
        return manager

    @classmethod
    @transaction.atomic
    def deactivate_manager(cls, manager: UserManager) -> None:
        """
        Soft deletes / deactivates a manager.
        """
        manager.is_active = False
        manager.save(update_fields=['is_active', 'updated_at'])
