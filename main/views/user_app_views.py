from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny

from main.permissions import IsAppUser
from main.serializers.user_app_serializers import (
    UserAppCreateSerializer,
    UserAppResponseSerializer,
    UserAppUpdateSerializer,
)
from main.services.user_app_service import UserAppService


class UserAppRegistrationView(APIView):
    """
    Endpoint for public registration of a new App User (Customer).
    """
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = UserAppCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user_app = UserAppService.create_user_app(serializer.validated_data)
        response_data = UserAppResponseSerializer(user_app).data

        return Response(
            {
                "status": "success",
                "status_code": status.HTTP_201_CREATED,
                "data": response_data
            },
            status=status.HTTP_201_CREATED
        )


class UserAppProfileView(APIView):
    """
    Endpoint for authenticated App User to view or update their own profile.
    """
    permission_classes = [IsAppUser]

    def get(self, request):
        serializer = UserAppResponseSerializer(request.user)
        return Response(
            {
                "status": "success",
                "status_code": status.HTTP_200_OK,
                "data": serializer.data
            },
            status=status.HTTP_200_OK
        )

    def put(self, request):
        serializer = UserAppUpdateSerializer(data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)

        updated_user_app = UserAppService.update_user_app(
            user_app=request.user,
            validated_data=serializer.validated_data
        )
        response_data = UserAppResponseSerializer(updated_user_app).data

        return Response(
            {
                "status": "success",
                "status_code": status.HTTP_200_OK,
                "data": response_data
            },
            status=status.HTTP_200_OK
        )
