from django.shortcuts import get_object_or_404
from main.models.queue import Queue
from main.models.restaurant import Restaurant


class QueueService:

    @staticmethod
    def get_or_create_queue(restaurant: Restaurant) -> Queue:
        queue, _ = Queue.objects.get_or_create(restaurant=restaurant)
        return queue

    @staticmethod
    def update_queue(queue: Queue, validated_data: dict) -> Queue:
        for field, value in validated_data.items():
            setattr(queue, field, value)
        queue.save()
        return queue

    @staticmethod
    def get_all_queues():
        return Queue.objects.select_related('restaurant').all()

    @staticmethod
    def get_manager_queues(manager):
        return Queue.objects.select_related('restaurant').filter(restaurant__manager=manager)
