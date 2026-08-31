from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny

from main.models.user_manager import UserManager
from main.permissions import IsManager, IsAdmin
from main.serializers.user_manager_serializers import (
    UserManagerCreateSerializer,
    UserManagerResponseSerializer,
    UserManagerUpdateSerializer,
    AdminUserManagerCreateSerializer,
    AdminUserManagerUpdateSerializer,
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


class AdminManagerListCreateView(APIView):
    permission_classes = [IsAdmin]

    def get(self, request):
        managers = UserManager.objects.all().order_by('-created_at')
        return Response({
            "status": "success",
            "data": UserManagerResponseSerializer(managers, many=True).data
        })

    def post(self, request):
        serializer = AdminUserManagerCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        manager = UserManagerService.create_manager(serializer.validated_data)
        return Response({
            "status": "success",
            "data": UserManagerResponseSerializer(manager).data
        }, status=status.HTTP_201_CREATED)


class AdminManagerDetailView(APIView):
    permission_classes = [IsAdmin]

    def get_object(self, pk):
        try:
            return UserManager.objects.get(pk=pk)
        except UserManager.DoesNotExist:
            return None

    def patch(self, request, pk):
        obj = self.get_object(pk)
        if not obj:
            return Response({"status": "error", "message": "Usuário não encontrado"}, status=404)
        serializer = AdminUserManagerUpdateSerializer(obj, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        for field, value in serializer.validated_data.items():
            setattr(obj, field, value)
        obj.save()
        return Response({
            "status": "success",
            "data": UserManagerResponseSerializer(obj).data
        })

    def delete(self, request, pk):
        obj = self.get_object(pk)
        if not obj:
            return Response({"status": "error", "message": "Usuário não encontrado"}, status=404)
        if obj.id == request.user.id:
            return Response({"status": "error", "message": "Você não pode excluir sua própria conta"}, status=400)
        obj.is_active = False
        obj.save(update_fields=['is_active', 'updated_at'])
        return Response({"status": "success", "message": "Usuário desativado"})
