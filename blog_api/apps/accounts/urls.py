from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView, TokenVerifyView

from .views import (
    RegisterView,
    CustomTokenObtainPairView,
    LogoutView,
    ProfileView,
    ChangePasswordView,
)

app_name = "accounts"

urlpatterns = [
    # Registration & auth
    path("register/",        RegisterView.as_view(),               name="register"),
    path("token/",           CustomTokenObtainPairView.as_view(),  name="token-obtain"),
    path("token/refresh/",   TokenRefreshView.as_view(),           name="token-refresh"),
    path("token/verify/",    TokenVerifyView.as_view(),            name="token-verify"),
    path("logout/",          LogoutView.as_view(),                 name="logout"),

    # Profile
    path("profile/",         ProfileView.as_view(),                name="profile"),
    path("profile/change-password/", ChangePasswordView.as_view(), name="change-password"),
]
