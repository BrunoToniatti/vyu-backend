from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from main.permissions import IsAdmin, IsManager
from main.serializers.queue_serializers import QueueSerializer, QueueUpdateSerializer
from main.services.queue_service import QueueService
from main.services.restaurant_service import RestaurantService


class AdminQueueListView(APIView):
    """
    Admin: list all queues across all restaurants.
    """
    permission_classes = [IsAdmin]

    def get(self, request):
        queues = QueueService.get_all_queues()
        serializer = QueueSerializer(queues, many=True)
        return Response({"status": "success", "status_code": 200, "count": queues.count(), "data": serializer.data})


class AdminQueueDetailView(APIView):
    """
    Admin: get or update any restaurant's queue.
    """
    permission_classes = [IsAdmin]

    def get(self, request, restaurant_pk):
        from main.models.restaurant import Restaurant
        from django.shortcuts import get_object_or_404
        restaurant = get_object_or_404(Restaurant, pk=restaurant_pk)
        queue = QueueService.get_or_create_queue(restaurant)
        return Response({"status": "success", "status_code": 200, "data": QueueSerializer(queue).data})

    def put(self, request, restaurant_pk):
        from main.models.restaurant import Restaurant
        from django.shortcuts import get_object_or_404
        restaurant = get_object_or_404(Restaurant, pk=restaurant_pk)
        queue = QueueService.get_or_create_queue(restaurant)
        serializer = QueueUpdateSerializer(data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        queue = QueueService.update_queue(queue, serializer.validated_data)
        return Response({"status": "success", "status_code": 200, "data": QueueSerializer(queue).data})


class ManagerQueueView(APIView):
    """
    Manager: get or update the queue of one of their own restaurants.
    """
    permission_classes = [IsManager]

    def get(self, request, restaurant_pk):
        restaurant = RestaurantService.get_restaurant_for_manager(request.user, restaurant_pk)
        queue = QueueService.get_or_create_queue(restaurant)
        return Response({"status": "success", "status_code": 200, "data": QueueSerializer(queue).data})

    def put(self, request, restaurant_pk):
        restaurant = RestaurantService.get_restaurant_for_manager(request.user, restaurant_pk)
        queue = QueueService.get_or_create_queue(restaurant)
        serializer = QueueUpdateSerializer(data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        queue = QueueService.update_queue(queue, serializer.validated_data)
        return Response({"status": "success", "status_code": 200, "data": QueueSerializer(queue).data})
