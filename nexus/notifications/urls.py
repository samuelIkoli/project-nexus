from django.urls import path
from .views import health_check, welcome

urlpatterns = [
    path("welcome/", welcome, name="welcome"),
    path("health/", health_check, name="health"),
]
