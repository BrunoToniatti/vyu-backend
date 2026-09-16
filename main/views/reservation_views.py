from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404

from main.permissions import IsManager, IsRestaurantOwner
from main.models.restaurant import Restaurant
from main.models.reservation import Reservation
from main.models.user_app import UserApp
from main.serializers.reservation_serializers import (
    ReservationSerializer,
    ReservationCreateSerializer,
    ReservationStatusSerializer,
)


class UserPhoneSearchView(APIView):
    """GET /reservations/user-search/?phone=<phone> — search app user by phone for auto-fill"""
    permission_classes = [IsManager]

    def get(self, request):
        phone = request.query_params.get('phone', '').strip()
        if len(phone) < 8:
            return Response({'status': 'success', 'data': None})
        # Normalize: strip non-digits for comparison
        digits = ''.join(c for c in phone if c.isdigit())
        user = UserApp.objects.filter(phone_number__icontains=digits[:8]).first()
        if not user:
            return Response({'status': 'success', 'data': None})
        return Response({
            'status': 'success',
            'data': {
                'id': user.id,
                'name': f"{user.first_name} {user.last_name}".strip(),
                'email': user.email,
                'phone': user.phone_number,
            },
        })


class ManagerReservationListCreateView(APIView):
    """GET/POST /restaurants/<pk>/reservations/ — manager lists and creates reservations"""
    permission_classes = [IsManager, IsRestaurantOwner]

    def get(self, request, pk):
        restaurant = get_object_or_404(Restaurant, pk=pk, manager=request.user)
        date_filter = request.query_params.get('date')
        status_filter = request.query_params.get('status')

        qs = Reservation.objects.filter(restaurant=restaurant).select_related('user_app')
        if date_filter:
            qs = qs.filter(date=date_filter)
        if status_filter:
            qs = qs.filter(status=status_filter)

        serializer = ReservationSerializer(qs, many=True)
        return Response({'status': 'success', 'status_code': 200, 'count': qs.count(), 'data': serializer.data})

    def post(self, request, pk):
        restaurant = get_object_or_404(Restaurant, pk=pk, manager=request.user)
        serializer = ReservationCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Try to link to an app user by phone
        phone = serializer.validated_data.get('guest_phone', '')
        digits = ''.join(c for c in phone if c.isdigit())
        user_app = None
        if len(digits) >= 8:
            user_app = UserApp.objects.filter(phone_number__icontains=digits[:8]).first()

        reservation = Reservation.objects.create(
            restaurant=restaurant,
            user_app=user_app,
            **serializer.validated_data,
        )
        return Response(
            {'status': 'success', 'status_code': 201, 'data': ReservationSerializer(reservation).data},
            status=status.HTTP_201_CREATED,
        )


class ManagerReservationDetailView(APIView):
    """PATCH/DELETE /restaurants/<pk>/reservations/<res_pk>/"""
    permission_classes = [IsManager, IsRestaurantOwner]

    def patch(self, request, pk, res_pk):
        restaurant = get_object_or_404(Restaurant, pk=pk, manager=request.user)
        reservation = get_object_or_404(Reservation, pk=res_pk, restaurant=restaurant)
        serializer = ReservationStatusSerializer(reservation, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({'status': 'success', 'data': ReservationSerializer(reservation).data})

    def delete(self, request, pk, res_pk):
        restaurant = get_object_or_404(Restaurant, pk=pk, manager=request.user)
        reservation = get_object_or_404(Reservation, pk=res_pk, restaurant=restaurant)
        reservation.delete()
        return Response({'status': 'success', 'message': 'Reserva removida.'}, status=status.HTTP_204_NO_CONTENT)
