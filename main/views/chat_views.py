from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny

from main.permissions import IsAppUser, IsManager, IsRestaurantOwner
from main.models.restaurant import Restaurant
from main.models.chat_message import ChatMessage


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
        if not Restaurant.objects.filter(pk=pk).exists():
            return Response({'status': 'error', 'message': 'Restaurante não encontrado.'}, status=404)

        since = request.query_params.get('since')
        qs = ChatMessage.objects.filter(restaurant_id=pk).select_related('user_app', 'restaurant')
        if since:
            qs = qs.filter(id__gt=since)
        else:
            qs = qs.order_by('-created_at')[:100]
            qs = list(reversed(list(qs)))

        return Response({
            'status': 'success',
            'status_code': 200,
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

        since = request.query_params.get('since')
        qs = ChatMessage.objects.filter(restaurant=restaurant).select_related('user_app', 'restaurant')
        if since:
            qs = qs.filter(id__gt=since)
        else:
            qs = qs.order_by('-created_at')[:100]
            qs = list(reversed(list(qs)))

        return Response({'status': 'success', 'status_code': 200, 'data': [_serialize_message(m) for m in qs]})

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
