from django.contrib import admin

from .models import Course, Lesson, Enrollment, CourseReview, TeacherReview


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ("title", "teacher", "price", "is_published", "created_at")
    search_fields = ("title", "teacher__email")
    list_filter = ("is_published",)


@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ("title", "course", "position", "created_at")
    list_filter = ("course",)
    ordering = ("course", "position")


@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ("learner", "course", "status", "created_at")
    list_filter = ("status",)
    search_fields = ("learner__email", "course__title")


@admin.register(CourseReview)
class CourseReviewAdmin(admin.ModelAdmin):
    list_display = ("course", "learner", "rating", "created_at")
    list_filter = ("rating",)
    search_fields = ("course__title", "learner__email")


@admin.register(TeacherReview)
class TeacherReviewAdmin(admin.ModelAdmin):
    list_display = ("teacher", "learner", "rating", "created_at")
    list_filter = ("rating",)
    search_fields = ("teacher__email", "learner__email")
