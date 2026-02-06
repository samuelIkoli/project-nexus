from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings

from payments.models import Payment
from courses.models import Enrollment


@shared_task
def send_payment_receipt(payment_id: int):
    """
    Send a simple payment receipt email.
    Uses console backend by default (prints to stdout) unless configured otherwise.
    """
    payment = Payment.objects.select_related("learner", "course").get(id=payment_id)
    subject = f"Payment receipt for {payment.course.title}"
    message = (
        f"Hi {payment.learner.email},\n\n"
        f"We received your payment of ${payment.amount} for {payment.course.title}.\n"
        f"Reference: {payment.reference}\n\n"
        "Thank you for learning with Project NExus!"
    )
    send_mail(
        subject,
        message,
        getattr(settings, "DEFAULT_FROM_EMAIL", "noreply@nexus.local"),
        [payment.learner.email],
        fail_silently=True,
    )
    return f"Sent payment receipt to {payment.learner.email}"


@shared_task
def send_enrollment_notification(enrollment_id: int):
    enrollment = Enrollment.objects.select_related("learner", "course").get(id=enrollment_id)
    subject = f"Enrollment update for {enrollment.course.title}"
    message = (
        f"Hi {enrollment.learner.email},\n\n"
        f"Your enrollment status for {enrollment.course.title} is now {enrollment.status}.\n"
    )
    send_mail(
        subject,
        message,
        getattr(settings, "DEFAULT_FROM_EMAIL", "noreply@nexus.local"),
        [enrollment.learner.email],
        fail_silently=True,
    )
    return f"Sent enrollment notification to {enrollment.learner.email}"
