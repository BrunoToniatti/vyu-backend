from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from main.models import Category, CategoryItem, UserApp, Restaurant
from main.serializers.category_serializers import (
    CategorySerializer, CategoryCreateSerializer,
    CategoryItemSerializer, CategoryItemCreateSerializer,
    UserPreferencesSerializer, RestaurantCategoryItemsSerializer,
)
from main.permissions import IsAdmin, IsManager, IsAppUser


# ── Admin: CRUD Categorias ──────────────────────────────────────────────────

class CategoryListCreateView(APIView):
    def get_permissions(self):
        if self.request.method == 'GET':
            return []
        return [IsAdmin()]

    def get(self, request):
        categories = Category.objects.filter(is_active=True).prefetch_related('items')
        return Response({
            'status': 'success',
            'data': CategorySerializer(categories, many=True).data
        })

    def post(self, request):
        serializer = CategoryCreateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({'status': 'error', 'errors': serializer.errors}, status=400)
        category = serializer.save()
        return Response({
            'status': 'success',
            'data': CategorySerializer(category).data
        }, status=201)


class CategoryDetailView(APIView):
    def get_permissions(self):
        if self.request.method == 'GET':
            return []
        return [IsAdmin()]

    def get_object(self, pk):
        try:
            return Category.objects.get(pk=pk)
        except Category.DoesNotExist:
            return None

    def get(self, request, pk):
        obj = self.get_object(pk)
        if not obj:
            return Response({'status': 'error', 'message': 'Categoria não encontrada'}, status=404)
        return Response({'status': 'success', 'data': CategorySerializer(obj).data})

    def patch(self, request, pk):
        obj = self.get_object(pk)
        if not obj:
            return Response({'status': 'error', 'message': 'Categoria não encontrada'}, status=404)
        serializer = CategoryCreateSerializer(obj, data=request.data, partial=True)
        if not serializer.is_valid():
            return Response({'status': 'error', 'errors': serializer.errors}, status=400)
        serializer.save()
        return Response({'status': 'success', 'data': CategorySerializer(obj).data})

    def delete(self, request, pk):
        obj = self.get_object(pk)
        if not obj:
            return Response({'status': 'error', 'message': 'Categoria não encontrada'}, status=404)
        obj.delete()
        return Response({'status': 'success'}, status=204)


# ── Admin: CRUD Itens ───────────────────────────────────────────────────────

class CategoryItemListCreateView(APIView):
    def get_permissions(self):
        if self.request.method == 'GET':
            return []
        return [IsAdmin()]

    def get(self, request, category_pk):
        items = CategoryItem.objects.filter(category_id=category_pk, is_active=True)
        return Response({'status': 'success', 'data': CategoryItemSerializer(items, many=True).data})

    def post(self, request, category_pk):
        data = {**request.data, 'category': category_pk}
        serializer = CategoryItemCreateSerializer(data=data)
        if not serializer.is_valid():
            return Response({'status': 'error', 'errors': serializer.errors}, status=400)
        item = serializer.save()
        return Response({'status': 'success', 'data': CategoryItemSerializer(item).data}, status=201)


class CategoryItemDetailView(APIView):
    permission_classes = [IsAdmin]

    def get_object(self, pk):
        try:
            return CategoryItem.objects.get(pk=pk)
        except CategoryItem.DoesNotExist:
            return None

    def patch(self, request, category_pk, pk):
        obj = self.get_object(pk)
        if not obj:
            return Response({'status': 'error', 'message': 'Item não encontrado'}, status=404)
        serializer = CategoryItemCreateSerializer(obj, data=request.data, partial=True)
        if not serializer.is_valid():
            return Response({'status': 'error', 'errors': serializer.errors}, status=400)
        serializer.save()
        return Response({'status': 'success', 'data': CategoryItemSerializer(obj).data})

    def delete(self, request, category_pk, pk):
        obj = self.get_object(pk)
        if not obj:
            return Response({'status': 'error', 'message': 'Item não encontrado'}, status=404)
        obj.delete()
        return Response({'status': 'success'}, status=204)


# ── UserApp: salvar preferências ────────────────────────────────────────────

class UserPreferencesView(APIView):
    permission_classes = [IsAppUser]

    def get(self, request):
        user = request.user
        items = user.preferences.select_related('category').filter(is_active=True)
        return Response({'status': 'success', 'data': CategoryItemSerializer(items, many=True).data})

    def put(self, request):
        serializer = UserPreferencesSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({'status': 'error', 'errors': serializer.errors}, status=400)
        ids = serializer.validated_data['preference_ids']
        items = CategoryItem.objects.filter(id__in=ids, is_active=True)
        request.user.preferences.set(items)
        return Response({'status': 'success', 'message': 'Preferências salvas'})


# ── Restaurant: gerenciar categorias ───────────────────────────────────────

class RestaurantCategoryItemsView(APIView):
    permission_classes = [IsManager]

    def get(self, request, restaurant_pk):
        try:
            restaurant = Restaurant.objects.get(pk=restaurant_pk, manager=request.user)
        except Restaurant.DoesNotExist:
            return Response({'status': 'error', 'message': 'Restaurante não encontrado'}, status=404)
        items = restaurant.category_items.select_related('category').filter(is_active=True)
        return Response({'status': 'success', 'data': CategoryItemSerializer(items, many=True).data})

    def put(self, request, restaurant_pk):
        try:
            restaurant = Restaurant.objects.get(pk=restaurant_pk, manager=request.user)
        except Restaurant.DoesNotExist:
            return Response({'status': 'error', 'message': 'Restaurante não encontrado'}, status=404)
        serializer = RestaurantCategoryItemsSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({'status': 'error', 'errors': serializer.errors}, status=400)
        ids = serializer.validated_data['category_item_ids']
        items = CategoryItem.objects.filter(id__in=ids, is_active=True)
        restaurant.category_items.set(items)
        return Response({'status': 'success', 'message': 'Categorias do restaurante atualizadas'})
