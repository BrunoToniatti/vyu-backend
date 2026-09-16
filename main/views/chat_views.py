from datetime import timedelta

from django.utils import timezone
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny

from main.permissions import IsAppUser, IsManager, IsRestaurantOwner
from main.models.restaurant import Restaurant
from main.models.chat_message import ChatMessage

CHAT_RESET_HOURS = 2


def _get_or_init_reset(restaurant: Restaurant):
    """Return (next_reset_at, was_reset). Resets messages if cycle expired."""
    now = timezone.now()
    if restaurant.chat_last_reset_at is None:
        restaurant.chat_last_reset_at = now
        restaurant.save(update_fields=['chat_last_reset_at'])
        return now + timedelta(hours=CHAT_RESET_HOURS), False

    next_reset = restaurant.chat_last_reset_at + timedelta(hours=CHAT_RESET_HOURS)
    if now >= next_reset:
        ChatMessage.objects.filter(restaurant=restaurant).delete()
        restaurant.chat_last_reset_at = now
        restaurant.save(update_fields=['chat_last_reset_at'])
        return now + timedelta(hours=CHAT_RESET_HOURS), True

    return next_reset, False


def _serialize_message(msg):
    return {
        'id': msg.id,
        'sender_type': msg.sender_type,
        'sender_name': msg.user_app.first_name if msg.user_app else msg.restaurant.name,
        'sender_photo': msg.user_app.photo_url if msg.user_app else msg.restaurant.photo_url,
        'text': msg.text,
        'created_at': msg.created_at.isoformat(),
    }


class PublicChatListView(APIView):
    """GET /restaurants/public/<pk>/chat/ — list last 100 messages (public read)"""
    permission_classes = [AllowAny]

    def get(self, request, pk):
        try:
            restaurant = Restaurant.objects.get(pk=pk)
        except Restaurant.DoesNotExist:
            return Response({'status': 'error', 'message': 'Restaurante não encontrado.'}, status=404)

        next_reset_at, was_reset = _get_or_init_reset(restaurant)

        since = request.query_params.get('since')
        qs = ChatMessage.objects.filter(restaurant_id=pk).select_related('user_app', 'restaurant')
        if since and not was_reset:
            qs = qs.filter(id__gt=since)
        else:
            qs = qs.order_by('-created_at')[:100]
            qs = list(reversed(list(qs)))

        return Response({
            'status': 'success',
            'status_code': 200,
            'next_reset_at': next_reset_at.isoformat(),
            'was_reset': was_reset,
            'data': [_serialize_message(m) for m in qs],
        })


class AppUserChatView(APIView):
    """POST /restaurants/public/<pk>/chat/ — send message as app user"""
    permission_classes = [IsAppUser]

    def post(self, request, pk):
        try:
            restaurant = Restaurant.objects.get(pk=pk)
        except Restaurant.DoesNotExist:
            return Response({'status': 'error', 'message': 'Restaurante não encontrado.'}, status=404)

        text = (request.data.get('text') or '').strip()
        if not text:
            return Response({'status': 'error', 'message': 'Mensagem vazia.'}, status=400)
        if len(text) > 1000:
            return Response({'status': 'error', 'message': 'Mensagem muito longa (máx. 1000 caracteres).'}, status=400)

        msg = ChatMessage.objects.create(
            restaurant=restaurant,
            user_app=request.user,
            sender_type=ChatMessage.SENDER_APP_USER,
            text=text,
        )
        return Response({'status': 'success', 'status_code': 201, 'data': _serialize_message(msg)}, status=201)


class ManagerChatView(APIView):
    """GET+POST /restaurants/<pk>/chat/ — manager reads and replies as restaurant"""
    permission_classes = [IsManager, IsRestaurantOwner]

    def get(self, request, pk):
        try:
            restaurant = Restaurant.objects.get(pk=pk, manager=request.user)
        except Restaurant.DoesNotExist:
            return Response({'status': 'error', 'message': 'Restaurante não encontrado.'}, status=404)

        next_reset_at, was_reset = _get_or_init_reset(restaurant)

        since = request.query_params.get('since')
        qs = ChatMessage.objects.filter(restaurant=restaurant).select_related('user_app', 'restaurant')
        if since and not was_reset:
            qs = qs.filter(id__gt=since)
        else:
            qs = qs.order_by('-created_at')[:100]
            qs = list(reversed(list(qs)))

        return Response({
            'status': 'success',
            'status_code': 200,
            'next_reset_at': next_reset_at.isoformat(),
            'was_reset': was_reset,
            'data': [_serialize_message(m) for m in qs],
        })

    def post(self, request, pk):
        try:
            restaurant = Restaurant.objects.get(pk=pk, manager=request.user)
        except Restaurant.DoesNotExist:
            return Response({'status': 'error', 'message': 'Restaurante não encontrado.'}, status=404)

        self.check_object_permissions(request, restaurant)

        text = (request.data.get('text') or '').strip()
        if not text:
            return Response({'status': 'error', 'message': 'Mensagem vazia.'}, status=400)

        msg = ChatMessage.objects.create(
            restaurant=restaurant,
            user_app=None,
            sender_type=ChatMessage.SENDER_RESTAURANT,
            text=text,
        )
        return Response({'status': 'success', 'status_code': 201, 'data': _serialize_message(msg)}, status=201)

    def delete(self, request, pk):
        """DELETE /restaurants/<pk>/chat/<msg_id>/ — manager deletes any message"""
        msg_id = request.query_params.get('msg_id')
        if not msg_id:
            return Response({'status': 'error', 'message': 'msg_id obrigatório.'}, status=400)
        try:
            restaurant = Restaurant.objects.get(pk=pk, manager=request.user)
            msg = ChatMessage.objects.get(pk=msg_id, restaurant=restaurant)
        except (Restaurant.DoesNotExist, ChatMessage.DoesNotExist):
            return Response({'status': 'error', 'message': 'Mensagem não encontrada.'}, status=404)

        msg.delete()
        return Response({'status': 'success', 'message': 'Mensagem removida.'})
