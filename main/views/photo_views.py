import os
import cloudinary
import cloudinary.uploader
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from main.permissions import IsManager, IsRestaurantOwner, IsAppUser
from main.models.restaurant import Restaurant
from main.serializers.restaurant_serializers import RestaurantAdminResponseSerializer
from main.serializers.user_app_serializers import UserAppResponseSerializer


def _configure_cloudinary():
    cloudinary.config(
        cloud_name=os.environ.get('CLOUDINARY_CLOUD_NAME'),
        api_key=os.environ.get('CLOUDINARY_API_KEY'),
        api_secret=os.environ.get('CLOUDINARY_API_SECRET'),
        secure=True,
    )


class RestaurantPhotoUploadView(APIView):
    permission_classes = [IsManager, IsRestaurantOwner]

    def post(self, request, pk):
        try:
            restaurant = Restaurant.objects.get(pk=pk, manager=request.user)
        except Restaurant.DoesNotExist:
            return Response(
                {'status': 'error', 'message': 'Restaurante não encontrado.'},
                status=status.HTTP_404_NOT_FOUND,
            )

        self.check_object_permissions(request, restaurant)

        photo = request.FILES.get('photo')
        if not photo:
            return Response(
                {'status': 'error', 'message': 'Nenhuma foto enviada.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        allowed_types = ['image/jpeg', 'image/png', 'image/webp', 'image/gif']
        if photo.content_type not in allowed_types:
            return Response(
                {'status': 'error', 'message': 'Formato inválido. Use JPG, PNG ou WebP.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if photo.size > 5 * 1024 * 1024:
            return Response(
                {'status': 'error', 'message': 'Foto muito grande. Máximo 5 MB.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        _configure_cloudinary()

        result = cloudinary.uploader.upload(
            photo,
            folder='vyu/restaurants',
            public_id=f'restaurant_{pk}',
            overwrite=True,
            resource_type='image',
            transformation=[
                {'width': 1200, 'height': 800, 'crop': 'limit', 'quality': 'auto', 'fetch_format': 'auto'}
            ],
        )

        restaurant.photo_url = result['secure_url']
        restaurant.save(update_fields=['photo_url'])

        serializer = RestaurantAdminResponseSerializer(restaurant)
        return Response(
            {'status': 'success', 'status_code': 200, 'data': serializer.data},
            status=status.HTTP_200_OK,
        )

    def delete(self, request, pk):
        try:
            restaurant = Restaurant.objects.get(pk=pk, manager=request.user)
        except Restaurant.DoesNotExist:
            return Response(
                {'status': 'error', 'message': 'Restaurante não encontrado.'},
                status=status.HTTP_404_NOT_FOUND,
            )

        self.check_object_permissions(request, restaurant)

        if restaurant.photo_url:
            _configure_cloudinary()
            cloudinary.uploader.destroy(f'vyu/restaurants/restaurant_{pk}')

        restaurant.photo_url = None
        restaurant.save(update_fields=['photo_url'])

        return Response({'status': 'success', 'message': 'Foto removida.'}, status=status.HTTP_200_OK)


class UserPhotoUploadView(APIView):
    permission_classes = [IsAppUser]

    def post(self, request):
        photo = request.FILES.get('photo')
        if not photo:
            return Response(
                {'status': 'error', 'message': 'Nenhuma foto enviada.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        allowed_types = ['image/jpeg', 'image/png', 'image/webp']
        if photo.content_type not in allowed_types:
            return Response(
                {'status': 'error', 'message': 'Formato inválido. Use JPG, PNG ou WebP.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if photo.size > 5 * 1024 * 1024:
            return Response(
                {'status': 'error', 'message': 'Foto muito grande. Máximo 5 MB.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        _configure_cloudinary()

        user = request.user
        result = cloudinary.uploader.upload(
            photo,
            folder='vyu/users',
            public_id=f'user_{user.id}',
            overwrite=True,
            resource_type='image',
            transformation=[
                {'width': 400, 'height': 400, 'crop': 'fill', 'gravity': 'face', 'quality': 'auto', 'fetch_format': 'auto'}
            ],
        )

        user.photo_url = result['secure_url']
        user.save(update_fields=['photo_url'])

        serializer = UserAppResponseSerializer(user)
        return Response(
            {'status': 'success', 'status_code': 200, 'data': serializer.data},
            status=status.HTTP_200_OK,
        )

    def delete(self, request):
        user = request.user
        if user.photo_url:
            _configure_cloudinary()
            cloudinary.uploader.destroy(f'vyu/users/user_{user.id}')

        user.photo_url = None
        user.save(update_fields=['photo_url'])

        return Response({'status': 'success', 'message': 'Foto removida.'}, status=status.HTTP_200_OK)
