from django.urls import path
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.views import TokenRefreshView

from .views import LoginView, MeView, RegisterView


urlpatterns = [
    path("register/", RegisterView.as_view(), name="auth-register"),
    path("login/", LoginView.as_view(), name="auth-login"),
    path(
        "token/refresh/",
        TokenRefreshView.as_view(authentication_classes=[], permission_classes=[AllowAny]),
        name="auth-token-refresh",
    ),
    path("me/", MeView.as_view(), name="auth-me"),
]
