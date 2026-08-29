import logging
from django.conf import settings
from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status

logger = logging.getLogger(__name__)


def custom_exception_handler(exc, context):
    """
    Custom DRF exception handler ensuring consistent error formats
    and preventing internal information/stack trace leakage in production.
    """
    response = exception_handler(exc, context)

    if response is not None:
        # Standardize payload structure
        customized_response = {
            "status": "error",
            "status_code": response.status_code,
            "errors": response.data if isinstance(response.data, (dict, list)) else {"detail": str(response.data)}
        }
        response.data = customized_response
        return response

    # Unhandled exceptions (500 Internal Server Error)
    logger.exception(f"Unhandled server exception in {context.get('view')}: {exc}")

    if settings.DEBUG:
        # Allow standard traceback in local debug mode
        return None

    # In production, return sanitized safe response without exposing internals
    return Response(
        {
            "status": "error",
            "status_code": status.HTTP_500_INTERNAL_SERVER_ERROR,
            "errors": {
                "detail": "Ocorreu um erro interno no servidor. Por favor, tente novamente mais tarde."
            }
        },
        status=status.HTTP_500_INTERNAL_SERVER_ERROR
    )
