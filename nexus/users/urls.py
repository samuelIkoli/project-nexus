from django.urls import path

from .views import RegisterView, EmailObtainAuthToken, ProfileView

urlpatterns = [
    path("register/", RegisterView.as_view(), name="register"),
    path("login/", EmailObtainAuthToken.as_view(), name="login"),
    path("profile/", ProfileView.as_view(), name="profile"),
]
