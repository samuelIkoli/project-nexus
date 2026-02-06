from rest_framework.routers import DefaultRouter

from .views import (
    CourseViewSet,
    LessonViewSet,
    EnrollmentViewSet,
    CourseReviewViewSet,
    TeacherReviewViewSet,
)

router = DefaultRouter()
router.register(r"courses", CourseViewSet, basename="course")
router.register(r"lessons", LessonViewSet, basename="lesson")
router.register(r"enrollments", EnrollmentViewSet, basename="enrollment")
router.register(r"course-reviews", CourseReviewViewSet, basename="course-review")
router.register(r"teacher-reviews", TeacherReviewViewSet, basename="teacher-review")

urlpatterns = router.urls
