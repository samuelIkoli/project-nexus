from django.db.models import Q
from rest_framework import permissions, viewsets, status
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema

from users.permissions import IsTeacher, IsLearner
from .models import Course, Lesson, Enrollment, CourseReview, TeacherReview
from .serializers import (
    CourseSerializer,
    LessonSerializer,
    EnrollmentSerializer,
    CourseReviewSerializer,
    TeacherReviewSerializer,
)


class CourseViewSet(viewsets.ModelViewSet):
    swagger_tags = ["Courses"]
    serializer_class = CourseSerializer

    def get_queryset(self):
        user = self.request.user
        qs = Course.objects.select_related("teacher").prefetch_related("lessons")

        if self.action in ["list", "retrieve"]:
            if user.is_authenticated and getattr(user, "role", None) == "TEACHER":
                return qs.filter(Q(is_published=True) | Q(teacher=user)).distinct()
            return qs.filter(is_published=True)

        if user.is_authenticated and getattr(user, "role", None) == "TEACHER":
            return qs.filter(teacher=user)
        return qs.none()

    def get_permissions(self):
        if self.action in ["list", "retrieve"]:
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated(), IsTeacher()]

    def perform_create(self, serializer):
        serializer.save(teacher=self.request.user)

    @action(detail=True, methods=["post"], permission_classes=[permissions.IsAuthenticated, IsTeacher])
    def publish(self, request, pk=None):
        course = self.get_object()
        course.is_published = True
        course.save(update_fields=["is_published", "updated_at"])
        return Response({"detail": "Course published"}, status=status.HTTP_200_OK)

    @action(detail=True, methods=["post"], permission_classes=[permissions.IsAuthenticated, IsTeacher])
    def unpublish(self, request, pk=None):
        course = self.get_object()
        course.is_published = False
        course.save(update_fields=["is_published", "updated_at"])
        return Response({"detail": "Course unpublished"}, status=status.HTTP_200_OK)


class LessonViewSet(viewsets.ModelViewSet):
    swagger_tags = ["Lessons"]
    serializer_class = LessonSerializer

    def get_queryset(self):
        qs = Lesson.objects.select_related("course", "course__teacher")
        course_id = self.request.query_params.get("course")
        if course_id:
            qs = qs.filter(course_id=course_id)

        user = self.request.user
        if user.is_authenticated and getattr(user, "role", None) == "TEACHER":
            return qs.filter(course__teacher=user)
        return qs.filter(course__is_published=True)

    def get_permissions(self):
        if self.action in ["list", "retrieve"]:
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated(), IsTeacher()]

    def perform_create(self, serializer):
        course = serializer.validated_data["course"]
        if course.teacher != self.request.user:
            raise PermissionDenied("You can only add lessons to your own courses.")
        serializer.save()

    def perform_update(self, serializer):
        course = serializer.instance.course
        if course.teacher != self.request.user:
            raise PermissionDenied("You can only update lessons in your own courses.")
        serializer.save()


class EnrollmentViewSet(viewsets.ModelViewSet):
    swagger_tags = ["Enrollments"]
    serializer_class = EnrollmentSerializer
    permission_classes = [permissions.IsAuthenticated]
    http_method_names = ["get", "post", "patch", "head", "options"]

    def get_queryset(self):
        user = self.request.user
        qs = Enrollment.objects.select_related("course", "course__teacher", "learner")
        if getattr(user, "role", None) == "TEACHER":
            return qs.filter(course__teacher=user)
        return qs.filter(learner=user)

    def create(self, request, *args, **kwargs):
        if getattr(request.user, "role", None) != "LEARNER":
            raise PermissionDenied("Only learners can enroll in courses.")
        return super().create(request, *args, **kwargs)

    def perform_create(self, serializer):
        enrollment = serializer.save(learner=self.request.user, status=Enrollment.Status.PENDING)
        try:
            from notifications.tasks import send_enrollment_notification

            send_enrollment_notification.delay(enrollment.id)
        except Exception:
            pass

    @action(detail=True, methods=["post"], permission_classes=[permissions.IsAuthenticated])
    def cancel(self, request, pk=None):
        enrollment = self.get_object()
        user = request.user
        if user != enrollment.learner and not (
            getattr(user, "role", None) == "TEACHER" and enrollment.course.teacher == user
        ):
            raise PermissionDenied("You cannot cancel this enrollment.")
        enrollment.status = Enrollment.Status.CANCELLED
        enrollment.save(update_fields=["status", "updated_at"])
        try:
            from notifications.tasks import send_enrollment_notification

            send_enrollment_notification.delay(enrollment.id)
        except Exception:
            pass
        return Response({"detail": "Enrollment cancelled."}, status=status.HTTP_200_OK)


class CourseReviewViewSet(viewsets.ModelViewSet):
    swagger_tags = ["Course Reviews"]
    serializer_class = CourseReviewSerializer
    http_method_names = ["get", "post", "patch", "delete", "head", "options"]

    def get_permissions(self):
        if self.action in ["list", "retrieve"]:
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated(), IsLearner()]

    def get_queryset(self):
        qs = CourseReview.objects.select_related("course", "learner", "course__teacher")
        course_id = self.request.query_params.get("course")
        teacher_id = self.request.query_params.get("teacher")
        if course_id:
            qs = qs.filter(course_id=course_id)
        if teacher_id:
            qs = qs.filter(course__teacher_id=teacher_id)
        return qs

    def perform_create(self, serializer):
        serializer.save(learner=self.request.user)

    def perform_update(self, serializer):
        if serializer.instance.learner != self.request.user:
            raise PermissionDenied("You can only edit your own review.")
        serializer.save()

    def perform_destroy(self, instance):
        if instance.learner != self.request.user:
            raise PermissionDenied("You can only delete your own review.")
        instance.delete()


class TeacherReviewViewSet(viewsets.ModelViewSet):
    swagger_tags = ["Teacher Reviews"]
    serializer_class = TeacherReviewSerializer
    http_method_names = ["get", "post", "patch", "delete", "head", "options"]

    def get_permissions(self):
        if self.action in ["list", "retrieve"]:
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated(), IsLearner()]

    def get_queryset(self):
        qs = TeacherReview.objects.select_related("teacher", "learner")
        teacher_id = self.request.query_params.get("teacher")
        if teacher_id:
            qs = qs.filter(teacher_id=teacher_id)
        return qs

    def perform_create(self, serializer):
        serializer.save(learner=self.request.user)

    def perform_update(self, serializer):
        if serializer.instance.learner != self.request.user:
            raise PermissionDenied("You can only edit your own review.")
        serializer.save()

    def perform_destroy(self, instance):
        if instance.learner != self.request.user:
            raise PermissionDenied("You can only delete your own review.")
        instance.delete()
