from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny

from main.permissions import IsManager
from main.serializers.user_manager_serializers import (
    UserManagerCreateSerializer,
    UserManagerResponseSerializer,
    UserManagerUpdateSerializer,
)
from main.services.user_manager_service import UserManagerService


class ManagerRegistrationView(APIView):
    """
    Endpoint for public registration of a new Manager.
    """
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = UserManagerCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        manager = UserManagerService.create_manager(serializer.validated_data)
        response_data = UserManagerResponseSerializer(manager).data

        return Response(
            {
                "status": "success",
                "status_code": status.HTTP_201_CREATED,
                "data": response_data
            },
            status=status.HTTP_201_CREATED
        )


class ManagerProfileView(APIView):
    """
    Endpoint for authenticated Manager to view or update their own profile.
    """
    permission_classes = [IsManager]

    def get(self, request):
        serializer = UserManagerResponseSerializer(request.user)
        return Response(
            {
                "status": "success",
                "status_code": status.HTTP_200_OK,
                "data": serializer.data
            },
            status=status.HTTP_200_OK
        )

    def put(self, request):
        serializer = UserManagerUpdateSerializer(data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)

        updated_manager = UserManagerService.update_manager(
            manager=request.user,
            validated_data=serializer.validated_data
        )
        response_data = UserManagerResponseSerializer(updated_manager).data

        return Response(
            {
                "status": "success",
                "status_code": status.HTTP_200_OK,
                "data": response_data
            },
            status=status.HTTP_200_OK
        )
