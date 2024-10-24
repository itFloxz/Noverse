from django.urls import path
from .views import RegisterUserView, TestAuthenticationView, VerifyUserEmail, LoginUserView, PasswordResetConfirm, PasswordResetRequestView, SetNewPassword, LogoutUserView, ChangePasswordView
from rest_framework_simplejwt.views import TokenRefreshView

from django.contrib import admin
from django.urls import path, include
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

urlpatterns = [
    path('register/', RegisterUserView.as_view(), name='register'),
    path('verify-email/',VerifyUserEmail.as_view(),name='verify'),
    path('login/',LoginUserView.as_view(),name='login'),
    path('profile/',TestAuthenticationView.as_view(),name='granted'),
    path('token/refresh/',TokenRefreshView.as_view(),name='refresh-token'),
    path('password-reset/', PasswordResetRequestView.as_view(), name='password-reset'),
    path('password-reset-confirm/<uidb64>/<token>/', PasswordResetConfirm.as_view(), name='password-reset-confirm'),
    path('set-new-password/', SetNewPassword.as_view(), name='set-new-password'),
    path('logout/', LogoutUserView.as_view(), name='logout'),
    path('change-password/', ChangePasswordView.as_view(), name='change-password'),
]
