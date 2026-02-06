from django.conf import settings
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator

User = settings.AUTH_USER_MODEL


class Course(models.Model):
    teacher = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="courses"
    )
    title = models.CharField(max_length=255)
    description = models.TextField()
    price = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    is_published = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return self.title


class Lesson(models.Model):
    course = models.ForeignKey(
        Course, on_delete=models.CASCADE, related_name="lessons"
    )
    title = models.CharField(max_length=255)
    video_url = models.URLField()
    position = models.PositiveIntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["position", "created_at"]

    def __str__(self) -> str:
        return f"{self.course.title} - {self.title}"


class Enrollment(models.Model):
    class Status(models.TextChoices):
        PENDING = "PENDING", "Pending"
        ACTIVE = "ACTIVE", "Active"
        CANCELLED = "CANCELLED", "Cancelled"

    learner = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="enrollments"
    )
    course = models.ForeignKey(
        Course, on_delete=models.CASCADE, related_name="enrollments"
    )
    status = models.CharField(
        max_length=20, choices=Status.choices, default=Status.PENDING
    )
    progress = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("learner", "course")
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"{self.learner} - {self.course}"


class CourseReview(models.Model):
    learner = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="course_reviews"
    )
    course = models.ForeignKey(
        Course, on_delete=models.CASCADE, related_name="reviews"
    )
    rating = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("learner", "course")
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"{self.course} ({self.rating}/5) by {self.learner}"


class TeacherReview(models.Model):
    learner = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="teacher_reviews"
    )
    teacher = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="reviews_received",
        limit_choices_to={"role": "TEACHER"},
    )
    rating = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("learner", "teacher")
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"{self.teacher} ({self.rating}/5) by {self.learner}"
