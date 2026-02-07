from rest_framework import permissions, viewsets
from rest_framework.exceptions import PermissionDenied
from drf_yasg.utils import swagger_auto_schema

from users.permissions import IsLearner
from .models import Payment
from .serializers import PaymentSerializer


class PaymentViewSet(viewsets.ModelViewSet):
    swagger_tags = ["Payments"]
    serializer_class = PaymentSerializer
    http_method_names = ["get", "post", "head", "options"]

    def get_permissions(self):
        if self.action in ["list", "retrieve"]:
            return [permissions.IsAuthenticated()]
        return [permissions.IsAuthenticated(), IsLearner()]

    def get_queryset(self):
        user = self.request.user
        qs = Payment.objects.select_related("course", "learner", "course__teacher")
        if getattr(user, "role", None) == "TEACHER":
            return qs.filter(course__teacher=user)
        return qs.filter(learner=user)

    def perform_create(self, serializer):
        user = self.request.user
        if getattr(user, "role", None) != "LEARNER":
            raise PermissionDenied("Only learners can initiate payments.")
        serializer.save()
