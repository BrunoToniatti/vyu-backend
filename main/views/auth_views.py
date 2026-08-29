from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.exceptions import TokenError

from main.throttling import LoginRateThrottle
from main.serializers.auth_serializers import (
    LoginRequestSerializer,
    TokenRefreshRequestSerializer,
)
from main.serializers.user_manager_serializers import UserManagerResponseSerializer
from main.serializers.user_app_serializers import UserAppResponseSerializer
from main.services.auth_service import AuthService


class ManagerLoginView(APIView):
    """
    Endpoint for Manager (Web) authentication.
    Issues JWT access & refresh tokens upon valid credentials.
    Protected by dedicated LoginRateThrottle to prevent brute force attacks.
    """
    permission_classes = [AllowAny]
    throttle_classes = [LoginRateThrottle]

    def post(self, request):
        serializer = LoginRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        identifier = serializer.validated_data['identifier']
        password = serializer.validated_data['password']

        auth_result = AuthService.authenticate_manager(identifier, password)

        if not auth_result:
            # Generic error message to prevent user enumeration attacks
            return Response(
                {
                    "status": "error",
                    "status_code": status.HTTP_401_UNAUTHORIZED,
                    "errors": {
                        "detail": "Credenciais inválidas. Verifique seu e-mail/usuário e senha."
                    }
                },
                status=status.HTTP_401_UNAUTHORIZED
            )

        user_data = UserManagerResponseSerializer(auth_result['user']).data

        return Response(
            {
                "status": "success",
                "status_code": status.HTTP_200_OK,
                "data": {
                    "access": auth_result['access'],
                    "refresh": auth_result['refresh'],
                    "user_type": auth_result['user_type'],
                    "user": user_data
                }
            },
            status=status.HTTP_200_OK
        )


class UserAppLoginView(APIView):
    """
    Endpoint for Consumer App (Mobile) authentication.
    Issues JWT access & refresh tokens upon valid credentials.
    Protected by dedicated LoginRateThrottle.
    """
    permission_classes = [AllowAny]
    throttle_classes = [LoginRateThrottle]

    def post(self, request):
        serializer = LoginRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        identifier = serializer.validated_data['identifier']
        password = serializer.validated_data['password']

        auth_result = AuthService.authenticate_user_app(identifier, password)

        if not auth_result:
            # Generic error message to prevent user enumeration attacks
            return Response(
                {
                    "status": "error",
                    "status_code": status.HTTP_401_UNAUTHORIZED,
                    "errors": {
                        "detail": "Credenciais inválidas. Verifique seu e-mail/usuário e senha."
                    }
                },
                status=status.HTTP_401_UNAUTHORIZED
            )

        user_data = UserAppResponseSerializer(auth_result['user']).data

        return Response(
            {
                "status": "success",
                "status_code": status.HTTP_200_OK,
                "data": {
                    "access": auth_result['access'],
                    "refresh": auth_result['refresh'],
                    "user_type": auth_result['user_type'],
                    "user": user_data
                }
            },
            status=status.HTTP_200_OK
        )


class TokenRefreshView(APIView):
    """
    Endpoint to refresh an expired JWT access token.
    """
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = TokenRefreshRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        refresh_token = serializer.validated_data['refresh']

        try:
            tokens = AuthService.refresh_access_token(refresh_token)
            return Response(
                {
                    "status": "success",
                    "status_code": status.HTTP_200_OK,
                    "data": tokens
                },
                status=status.HTTP_200_OK
            )
        except TokenError as e:
            return Response(
                {
                    "status": "error",
                    "status_code": status.HTTP_401_UNAUTHORIZED,
                    "errors": {
                        "detail": "Token de atualização inválido ou expirado."
                    }
                },
                status=status.HTTP_401_UNAUTHORIZED
            )
