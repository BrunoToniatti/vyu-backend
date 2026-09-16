from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404

from main.permissions import IsManager, IsRestaurantOwner, IsAppUser
from main.models.restaurant import Restaurant
from main.models.reservation import Reservation
from main.models.user_app import UserApp
from main.serializers.reservation_serializers import (
    ReservationSerializer,
    ReservationCreateSerializer,
    ReservationStatusSerializer,
    PublicReservationCreateSerializer,
    AppUserReservationSerializer,
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


class MyReservationsView(APIView):
    """GET /reservations/mine/ — all reservations for the authenticated app user"""
    permission_classes = [IsAppUser]

    def get(self, request):
        user: UserApp = request.user
        qs = (
            Reservation.objects.filter(user_app=user)
            .select_related('restaurant')
            .order_by('-date', '-time')
        )
        data = [
            {
                'id': r.id,
                'restaurant_id': r.restaurant.id,
                'restaurant_name': r.restaurant.name,
                'date': str(r.date),
                'time': str(r.time)[:5],
                'party_size': r.party_size,
                'notes': r.notes,
                'status': r.status,
                'status_display': r.get_status_display(),
            }
            for r in qs
        ]
        return Response({'status': 'success', 'data': data})


class PublicReservationCreateView(APIView):
    """POST /restaurants/public/<pk>/reservations/ — app user creates a reservation for themselves"""
    permission_classes = [IsAppUser]

    def post(self, request, pk):
        restaurant = get_object_or_404(Restaurant, pk=pk)
        serializer = PublicReservationCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user: UserApp = request.user
        reservation = Reservation.objects.create(
            restaurant=restaurant,
            user_app=user,
            guest_name=f"{user.first_name} {user.last_name}".strip() or user.username,
            guest_phone=user.phone_number or '',
            guest_email=user.email or '',
            **serializer.validated_data,
        )
        return Response(
            {'status': 'success', 'status_code': 201, 'data': AppUserReservationSerializer(reservation).data},
            status=status.HTTP_201_CREATED,
        )

    def get(self, request, pk):
        """GET own reservations for this restaurant"""
        restaurant = get_object_or_404(Restaurant, pk=pk)
        user: UserApp = request.user
        qs = Reservation.objects.filter(restaurant=restaurant, user_app=user).order_by('date', 'time')
        return Response({
            'status': 'success',
            'data': AppUserReservationSerializer(qs, many=True).data,
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
