from rest_framework import serializers
from django.contrib.auth import get_user_model

from users.serializers import UserSerializer
from .models import Course, Lesson, Enrollment, CourseReview, TeacherReview

User = get_user_model()


class LessonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lesson
        fields = ["id", "course", "title", "video_url", "position", "created_at", "updated_at"]
        read_only_fields = ["id", "created_at", "updated_at"]


class CourseSerializer(serializers.ModelSerializer):
    teacher = UserSerializer(read_only=True)
    lessons = LessonSerializer(many=True, read_only=True)

    class Meta:
        model = Course
        fields = [
            "id",
            "teacher",
            "title",
            "description",
            "price",
            "is_published",
            "lessons",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "teacher", "lessons", "created_at", "updated_at"]


class EnrollmentSerializer(serializers.ModelSerializer):
    course = CourseSerializer(read_only=True)
    course_id = serializers.PrimaryKeyRelatedField(
        queryset=Course.objects.filter(is_published=True),
        source="course",
        write_only=True,
    )

    class Meta:
        model = Enrollment
        fields = [
            "id",
            "course",
            "course_id",
            "status",
            "progress",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "course", "status", "progress", "created_at", "updated_at"]


class CourseReviewSerializer(serializers.ModelSerializer):
    learner = UserSerializer(read_only=True)
    course = CourseSerializer(read_only=True)
    course_id = serializers.PrimaryKeyRelatedField(
        queryset=Course.objects.filter(is_published=True),
        source="course",
        write_only=True,
    )

    class Meta:
        model = CourseReview
        fields = [
            "id",
            "learner",
            "course",
            "course_id",
            "rating",
            "comment",
            "created_at",
        ]
        read_only_fields = ["id", "learner", "course", "created_at"]

    def validate(self, attrs):
        request = self.context["request"]
        user = request.user
        course = attrs.get("course") or getattr(getattr(self, "instance", None), "course", None)
        if course is None:
            raise serializers.ValidationError("Course is required.")
        from .models import Enrollment

        has_active = Enrollment.objects.filter(
            learner=user, course=course, status=Enrollment.Status.ACTIVE
        ).exists()
        if not has_active:
            raise serializers.ValidationError(
                "You can only review courses you are actively enrolled in."
            )
        return attrs

    def create(self, validated_data):
        validated_data["learner"] = self.context["request"].user
        return super().create(validated_data)


class TeacherReviewSerializer(serializers.ModelSerializer):
    learner = UserSerializer(read_only=True)
    teacher = UserSerializer(read_only=True)
    teacher_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.none(), write_only=True
    )

    class Meta:
        model = TeacherReview
        fields = [
            "id",
            "learner",
            "teacher",
            "teacher_id",
            "rating",
            "comment",
            "created_at",
        ]
        read_only_fields = ["id", "learner", "teacher", "created_at"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # limit teacher_id choices to actual teachers
        self.fields["teacher_id"].queryset = User.objects.filter(role=User.Role.TEACHER)

    def validate(self, attrs):
        request = self.context["request"]
        user = request.user
        teacher = attrs.get("teacher_id") or getattr(getattr(self, "instance", None), "teacher", None)
        if teacher is None:
            raise serializers.ValidationError("Teacher is required.")
        from .models import Enrollment

        has_active = Enrollment.objects.filter(
            learner=user, course__teacher=teacher, status=Enrollment.Status.ACTIVE
        ).exists()
        if not has_active:
            raise serializers.ValidationError(
                "You can only review teachers for courses you are actively enrolled in."
            )
        attrs["teacher"] = teacher
        return attrs

    def create(self, validated_data):
        validated_data["learner"] = self.context["request"].user
        validated_data.pop("teacher_id", None)
        return super().create(validated_data)
