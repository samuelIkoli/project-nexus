from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema


@swagger_auto_schema(method="get", tags=["System"], operation_summary="Welcome message")
@api_view(["GET"])
@authentication_classes([])
@permission_classes([AllowAny])
def welcome(request):
    return Response({"message": "welcome to project Nexus"})


@swagger_auto_schema(method="get", tags=["System"], operation_summary="Health check")
@api_view(["GET"])
@authentication_classes([])
@permission_classes([AllowAny])
def health_check(request):
    return Response({"status": "Nexus backend running"})
