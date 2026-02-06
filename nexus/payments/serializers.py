from uuid import uuid4

from rest_framework import serializers

from courses.models import Course, Enrollment
from courses.serializers import CourseSerializer
from .models import Payment


class PaymentSerializer(serializers.ModelSerializer):
    course = CourseSerializer(read_only=True)
    course_id = serializers.PrimaryKeyRelatedField(
        queryset=Course.objects.filter(is_published=True),
        source="course",
        write_only=True,
    )

    class Meta:
        model = Payment
        fields = [
            "id",
            "course",
            "course_id",
            "amount",
            "provider",
            "status",
            "reference",
            "metadata",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "course",
            "status",
            "reference",
            "metadata",
            "created_at",
            "updated_at",
        ]

    def create(self, validated_data):
        request = self.context["request"]
        user = request.user
        course = validated_data["course"]
        provider = validated_data.get("provider", "mock")
        amount = validated_data.get("amount") or course.price

        payment = Payment.objects.create(
            learner=user,
            course=course,
            amount=amount,
            provider=provider,
            status=Payment.Status.SUCCESS,
            reference=str(uuid4()),
            metadata={"note": "Simulated payment success"},
        )

        enrollment, _ = Enrollment.objects.get_or_create(
            learner=user, course=course, defaults={"status": Enrollment.Status.ACTIVE}
        )
        enrollment.status = Enrollment.Status.ACTIVE
        enrollment.save(update_fields=["status", "updated_at"])

        # Trigger async notification
        try:
            from notifications.tasks import send_payment_receipt
            from notifications.tasks import send_enrollment_notification

            send_payment_receipt.delay(payment.id)
            send_enrollment_notification.delay(enrollment.id)
        except Exception:
            # Fail silently; payment should not fail because email failed.
            pass

        return payment
