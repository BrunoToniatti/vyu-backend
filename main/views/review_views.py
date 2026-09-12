from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.exceptions import NotFound, PermissionDenied, ValidationError

from main.models.restaurant import Restaurant
from main.models.review import Review
from main.permissions import IsAppUser, IsManager, IsRestaurantOwner
from main.serializers.review_serializers import (
    ReviewCreateSerializer,
    ReviewResponseSerializer,
    ManagerResponseSerializer,
)


def get_restaurant_or_404(pk):
    try:
        return Restaurant.objects.get(pk=pk)
    except Restaurant.DoesNotExist:
        raise NotFound("Restaurante não encontrado.")


class RestaurantReviewListCreateView(APIView):
    def get_permissions(self):
        if self.request.method == 'GET':
            return [AllowAny()]
        return [IsAppUser()]

    def get(self, request, restaurant_pk):
        restaurant = get_restaurant_or_404(restaurant_pk)
        reviews = restaurant.reviews.select_related('user_app').all()
        serializer = ReviewResponseSerializer(reviews, many=True)
        return Response({
            "status": "success",
            "status_code": 200,
            "count": reviews.count(),
            "data": serializer.data,
        })

    def post(self, request, restaurant_pk):
        restaurant = get_restaurant_or_404(restaurant_pk)

        if Review.objects.filter(user_app=request.user, restaurant=restaurant).exists():
            raise ValidationError("Você já avaliou este restaurante.")

        serializer = ReviewCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        review = serializer.save(user_app=request.user, restaurant=restaurant)
        return Response({
            "status": "success",
            "status_code": 201,
            "data": ReviewResponseSerializer(review).data,
        }, status=status.HTTP_201_CREATED)


class ManagerReviewResponseView(APIView):
    permission_classes = [IsManager]

    def post(self, request, restaurant_pk, review_pk):
        restaurant = get_restaurant_or_404(restaurant_pk)
        if restaurant.manager_id != request.user.id:
            raise PermissionDenied("Você não é o gerente deste restaurante.")

        try:
            review = Review.objects.get(pk=review_pk, restaurant=restaurant)
        except Review.DoesNotExist:
            raise NotFound("Avaliação não encontrada.")

        serializer = ManagerResponseSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        review.manager_response = serializer.validated_data['response']
        review.save(update_fields=['manager_response'])

        return Response({
            "status": "success",
            "status_code": 200,
            "data": ReviewResponseSerializer(review).data,
        })
