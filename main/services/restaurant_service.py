from django.db import transaction
from django.db.models import Q
from rest_framework.exceptions import NotFound, PermissionDenied
from main.models.restaurant import Restaurant
from main.models.user_manager import UserManager


class RestaurantService:
    """
    Business logic layer for Restaurant entity.
    Enforces strict ownership checks and data isolation.
    """

    @classmethod
    @transaction.atomic
    def create_restaurant(cls, manager: UserManager, validated_data: dict) -> Restaurant:
        """
        Creates a new Restaurant owned by the authenticated manager.
        The manager association is strictly enforced from the server-side JWT context.
        """
        if not isinstance(manager, UserManager):
            raise PermissionDenied("Apenas gerentes autenticados podem criar restaurantes.")

        # Ignore any client-injected manager or manager_id
        validated_data.pop('manager', None)
        validated_data.pop('manager_id', None)

        restaurant = Restaurant.objects.create(
            manager=manager,
            **validated_data
        )
        return restaurant

    @classmethod
    def get_manager_restaurants(cls, manager: UserManager):
        """
        Returns all restaurants owned by the given manager.
        """
        if not isinstance(manager, UserManager):
            raise PermissionDenied("Apenas gerentes autenticados podem consultar seus restaurantes.")
        return Restaurant.objects.filter(manager=manager).order_by('-created_at')

    @classmethod
    def get_restaurant_for_manager(cls, manager: UserManager, restaurant_id: int) -> Restaurant:
        """
        Retrieves a restaurant for a manager, verifying ownership.
        Returns 404 or 403 if not found or not owned by this manager (IDOR protection).
        """
        if not isinstance(manager, UserManager):
            raise PermissionDenied("Apenas gerentes autenticados podem acessar esta área.")

        try:
            restaurant = Restaurant.objects.get(id=restaurant_id)
        except Restaurant.DoesNotExist:
            raise NotFound("Restaurante não encontrado.")

        # Strict IDOR / BOLA check
        if restaurant.manager_id != manager.id:
            raise PermissionDenied("Você não tem permissão para acessar os dados deste restaurante.")

        return restaurant

    @classmethod
    @transaction.atomic
    def update_restaurant(cls, manager: UserManager, restaurant: Restaurant, validated_data: dict) -> Restaurant:
        """
        Updates an existing restaurant, verifying manager ownership.
        """
        if not isinstance(manager, UserManager) or restaurant.manager_id != manager.id:
            raise PermissionDenied("Você não tem permissão para alterar este restaurante.")

        # Prevent modification of manager_id or id
        validated_data.pop('manager', None)
        validated_data.pop('manager_id', None)
        validated_data.pop('id', None)

        for field, value in validated_data.items():
            setattr(restaurant, field, value)

        restaurant.save()
        return restaurant

    @classmethod
    @transaction.atomic
    def delete_restaurant(cls, manager: UserManager, restaurant: Restaurant) -> None:
        """
        Deletes a restaurant, verifying manager ownership.
        """
        if not isinstance(manager, UserManager) or restaurant.manager_id != manager.id:
            raise PermissionDenied("Você não tem permissão para excluir este restaurante.")

        restaurant.delete()

    @classmethod
    def search_public_restaurants(cls, search_query: str = None):
        """
        Searches restaurants for public consumption.
        Supports simple string search across name, address, and CNPJ.
        """
        queryset = Restaurant.objects.all().order_by('-created_at')

        if search_query:
            clean_query = search_query.strip()
            if clean_query:
                queryset = queryset.filter(
                    Q(name__icontains=clean_query) |
                    Q(address__icontains=clean_query) |
                    Q(cnpj__icontains=clean_query)
                )

        return queryset

    @classmethod
    @transaction.atomic
    def transfer_restaurant(cls, restaurant: Restaurant, new_manager_id: int) -> Restaurant:
        """
        Admin-only: transfers restaurant ownership to another manager.
        """
        try:
            new_manager = UserManager.objects.get(id=new_manager_id)
        except UserManager.DoesNotExist:
            from rest_framework.exceptions import NotFound
            raise NotFound("Gerente de destino não encontrado.")
        restaurant.manager = new_manager
        restaurant.save()
        return restaurant

    @classmethod
    def get_all_restaurants(cls):
        """
        Admin-only: returns all restaurants.
        """
        return Restaurant.objects.select_related('manager').all().order_by('-created_at')

    @classmethod
    def get_public_restaurant(cls, restaurant_id: int) -> Restaurant:
        """
        Retrieves public information for a single restaurant.
        """
        try:
            return Restaurant.objects.get(id=restaurant_id)
        except Restaurant.DoesNotExist:
            raise NotFound("Restaurante não encontrado.")
