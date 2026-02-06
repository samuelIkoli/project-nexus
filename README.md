# 📚 Project Nexus — EdTech Learning Platform (Backend)

Project Nexus is a backend-powered EdTech platform built with Django that enables teachers to publish paid video courses and learners to purchase and access educational content.

The platform supports user authentication, course management, secure payment tracking, background task processing with Celery, and public API documentation via Swagger.

---

## 🚀 Features

### 👨‍🏫 For Teachers
- Register and manage accounts
- Create and publish courses
- Upload and organize video lessons
- Set course pricing
- Manage multiple courses

### 👩‍🎓 For Learners
- Register and onboard
- Browse available courses
- Purchase paid courses
- Access enrolled course materials
- Stream video lessons

### ⚙️ System Features
- RESTful API (Django REST Framework)
- Background processing with Celery
- Message broker with RabbitMQ
- Email notifications
- Secure payment tracking
- Public Swagger documentation
- Production-ready deployment

---

## 🛠️ Tech Stack

| Layer        | Technology |
|--------------|------------|
| Backend      | Django, Django REST Framework |
| Database     | SQLite (Development), PostgreSQL (Production) |
| Task Queue   | Celery |
| Message Broker | RabbitMQ |
| API Docs     | drf-yasg (Swagger) |
| Web Server   | Gunicorn |
| Static Files | WhiteNoise |
| Deployment   | Render / PythonAnywhere |

---

## 📐 System Architecture
Client (Frontend / API Consumer)
↓
Django REST API (Gunicorn)
↓
PostgreSQL Database
↓
Celery Workers
↓
RabbitMQ Broker

---

## 🗄️ Database Schema (MVP)

### Core Models

#### User
- id
- email
- password
- role (TEACHER / LEARNER)
- created_at

#### Course
- id
- teacher_id
- title
- description
- price
- is_published

#### Lesson
- id
- course_id
- title
- video_url
- position

#### Enrollment
- id
- learner_id
- course_id
- status

#### Payment
- id
- learner_id
- course_id
- amount
- provider
- status

#### CourseReview
- id
- learner_id
- course_id
- rating (1–5)
- comment
- created_at

#### TeacherReview
- id
- learner_id
- teacher_id
- rating (1–5)
- comment
- created_at
---

## 📁 Project Structure

nexus/
├── manage.py
├── requirements.txt
├── nexus/
│ ├── settings.py
│ ├── urls.py
│ ├── celery.py
│ └── wsgi.py
├── notifications/
│ ├── models.py
│ ├── views.py
│ ├── tasks.py
│ └── serializers.py
└── staticfiles/