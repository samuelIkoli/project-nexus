import random
from decimal import Decimal

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework.authtoken.models import Token

from courses.models import Course, Lesson, Enrollment, CourseReview, TeacherReview
from payments.models import Payment


PASSWORD = "password"


class Command(BaseCommand):
    help = "Seed the database with demo data for quick testing."

    def handle(self, *args, **options):
        User = get_user_model()

        teachers_data = [
            {"email": "teacher1@example.com", "first_name": "Ada", "last_name": "Lovelace"},
            {"email": "teacher2@example.com", "first_name": "Alan", "last_name": "Turing"},
        ]
        learners_data = [
            {"email": "learner1@example.com", "first_name": "Grace", "last_name": "Hopper"},
            {"email": "learner2@example.com", "first_name": "Katherine", "last_name": "Johnson"},
            {"email": "learner3@example.com", "first_name": "Tim", "last_name": "Berners-Lee"},
        ]

        teachers = []
        learners = []

        for data in teachers_data:
            user, created = User.objects.get_or_create(
                email=data["email"],
                defaults={
                    "role": User.Role.TEACHER,
                    "first_name": data["first_name"],
                    "last_name": data["last_name"],
                },
            )
            user.set_password(PASSWORD)
            user.save()
            teachers.append(user)
            Token.objects.get_or_create(user=user)
            self.stdout.write(self.style.SUCCESS(f"Teacher ready: {user.email}"))

        for data in learners_data:
            user, created = User.objects.get_or_create(
                email=data["email"],
                defaults={
                    "role": User.Role.LEARNER,
                    "first_name": data["first_name"],
                    "last_name": data["last_name"],
                },
            )
            user.set_password(PASSWORD)
            user.save()
            learners.append(user)
            Token.objects.get_or_create(user=user)
            self.stdout.write(self.style.SUCCESS(f"Learner ready: {user.email}"))

        courses_payload = [
            {
                "title": "Intro to Algorithms",
                "description": "Foundations of algorithms and problem solving.",
                "price": Decimal("49.00"),
            },
            {
                "title": "Distributed Systems 101",
                "description": "Concepts, trade-offs, and practical patterns.",
                "price": Decimal("59.00"),
            },
            {
                "title": "Web Security Basics",
                "description": "Secure coding, threats, and mitigations.",
                "price": Decimal("39.00"),
            },
        ]

        created_courses = []
        for payload, teacher in zip(courses_payload, teachers * 2):
            course, _ = Course.objects.get_or_create(
                title=payload["title"],
                defaults={
                    "teacher": teacher,
                    "description": payload["description"],
                    "price": payload["price"],
                    "is_published": True,
                },
            )
            created_courses.append(course)
            self.stdout.write(self.style.SUCCESS(f"Course ready: {course.title}"))

            # lessons
            for idx in range(1, 4):
                Lesson.objects.get_or_create(
                    course=course,
                    position=idx,
                    defaults={
                        "title": f"{course.title} - Lesson {idx}",
                        "video_url": f"https://videos.example.com/{course.id}/{idx}",
                    },
                )

        # Enroll learners, create payments, and reviews
        for learner in learners:
            for course in created_courses:
                enrollment, _ = Enrollment.objects.get_or_create(
                    learner=learner,
                    course=course,
                    defaults={"status": Enrollment.Status.ACTIVE},
                )
                Payment.objects.get_or_create(
                    learner=learner,
                    course=course,
                    defaults={
                        "amount": course.price,
                        "provider": "mock",
                        "status": Payment.Status.SUCCESS,
                        "reference": f"{course.id}-{learner.id}",
                        "metadata": {"seeded": True},
                    },
                )

                # Course review
                CourseReview.objects.get_or_create(
                    learner=learner,
                    course=course,
                    defaults={
                        "rating": random.randint(4, 5),
                        "comment": f"Learner {learner.first_name} enjoyed {course.title}.",
                        "created_at": timezone.now(),
                    },
                )

                # Teacher review
                TeacherReview.objects.get_or_create(
                    learner=learner,
                    teacher=course.teacher,
                    defaults={
                        "rating": random.randint(4, 5),
                        "comment": f"Instructor {course.teacher.first_name} explained topics clearly.",
                        "created_at": timezone.now(),
                    },
                )

        self.stdout.write(self.style.SUCCESS("Seeding complete."))
        self.stdout.write(self.style.SUCCESS(f"Test password for all users: {PASSWORD}"))
