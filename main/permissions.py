from rest_framework.permissions import BasePermission
from main.models.user_manager import UserManager
from main.models.user_app import UserApp


class IsAuthenticatedUser(BasePermission):
    """
    Allows access only to authenticated users (either UserManager or UserApp).
    """

    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated)


class IsManager(BasePermission):
    """
    Allows access only to authenticated Manager users.
    """

    def has_permission(self, request, view):
        return bool(
            request.user and
            request.user.is_authenticated and
            isinstance(request.user, UserManager) and
            getattr(request.user, 'user_type', None) == 'MANAGER'
        )


class IsAppUser(BasePermission):
    """
    Allows access only to authenticated App users (Customers).
    """

    def has_permission(self, request, view):
        return bool(
            request.user and
            request.user.is_authenticated and
            isinstance(request.user, UserApp) and
            getattr(request.user, 'user_type', None) == 'APP_USER'
        )


class IsAdmin(BasePermission):
    """
    Allows access only to authenticated Managers with is_admin=True.
    """
    def has_permission(self, request, view):
        return bool(
            request.user and
            request.user.is_authenticated and
            isinstance(request.user, UserManager) and
            getattr(request.user, 'is_admin', False)
        )


class IsRestaurantOwner(BasePermission):
    """
    Object-level permission to only allow the owning Manager to view, edit, or delete a restaurant.
    Strictly verifies BOTH user type (must be UserManager) AND matching manager_id ownership.
    """

    def has_permission(self, request, view):
        # Must be an authenticated manager first
        return bool(
            request.user and
            request.user.is_authenticated and
            isinstance(request.user, UserManager) and
            getattr(request.user, 'user_type', None) == 'MANAGER'
        )

    def has_object_permission(self, request, view, obj):
        # Strict dual-check: User type must be UserManager AND owner must match
        if not (
            request.user and
            request.user.is_authenticated and
            isinstance(request.user, UserManager) and
            getattr(request.user, 'user_type', None) == 'MANAGER'
        ):
            return False

        return obj.manager_id == request.user.id
