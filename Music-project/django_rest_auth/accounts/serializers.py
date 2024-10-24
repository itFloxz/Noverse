from rest_framework import serializers
from .models import User
from django.contrib.auth import authenticate
from rest_framework.exceptions import AuthenticationFailed
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.contrib.sites.shortcuts import get_current_site
from django.utils.encoding import smart_bytes, force_str
from django.urls import reverse
from .utils import send_normal_email
from rest_framework_simplejwt.tokens import RefreshToken, TokenError
from django.utils.html import format_html
import re


class UserRegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(max_length=68, min_length=6, write_only=True)
    password2 = serializers.CharField(max_length=68, min_length=6, write_only=True)

    class Meta:
        model = User
        fields = ['email', 'first_name', 'last_name', 'password', 'password2']

    def validate(self, attrs):
        password = attrs.get('password', '')
        password2 = attrs.get('password2', '')

        # ตรวจสอบว่ารหัสผ่านตรงกันหรือไม่
        if password != password2:
            raise serializers.ValidationError('Passwords do not match.')

        # ตรวจสอบความปลอดภัยของรหัสผ่าน
        if len(password) < 8:
            raise serializers.ValidationError('Password must be at least 8 characters long.')
        if not re.search(r'[A-Z]', password):
            raise serializers.ValidationError('Password must contain at least one uppercase letter.')
        if not re.search(r'[a-z]', password):
            raise serializers.ValidationError('Password must contain at least one lowercase letter.')
        if not re.search(r'[0-9]', password):
            raise serializers.ValidationError('Password must contain at least one digit.')
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            raise serializers.ValidationError('Password must contain at least one special character.')

        return attrs

    def create(self, validated_data):
        user = User.objects.create_user(
            email=validated_data['email'],
            first_name=validated_data.get('first_name'),
            last_name=validated_data.get('last_name'),
            password=validated_data['password']
        )
        return user


class LoginSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(max_length=255, min_length=6)
    password = serializers.CharField(max_length=68, write_only=True)
    full_name = serializers.CharField(max_length=255, read_only=True)
    access_token = serializers.CharField(max_length=255, read_only=True)
    refresh_token = serializers.CharField(max_length=255, read_only=True)

    class Meta:
        model = User
        fields = ['email', 'password', 'full_name', 'access_token', 'refresh_token']

    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')
        request = self.context.get('request')
        user = authenticate(request, email=email, password=password)
        if not user:
            raise AuthenticationFailed("Invalid credentials, try again")
        if not user.is_verified:
            raise AuthenticationFailed("Email is not verified")
        user_tokens = user.tokens()

        return {
            'email': user.email,
            'full_name': user.get_full_name,
            'access_token': str(user_tokens.get('access')),
            'refresh_token': str(user_tokens.get('refresh')),
        }


class PasswordResetRequestSerializer(serializers.Serializer):
    email = serializers.EmailField(max_length=255)

    class Meta:
        fields = ['email']

    def validate(self, attrs):
        email = attrs.get('email')
        if User.objects.filter(email=email).exists():
            user = User.objects.get(email=email)
            uidb64 = urlsafe_base64_encode(smart_bytes(user.id))
            token = PasswordResetTokenGenerator().make_token(user)
            abslink = f"http://localhost:5173/password-reset-confirm/{uidb64}/{token}"

            # Update email content to be more formal and styled
            email_body = f'''
<html>
  <body style="margin: 0; padding: 0; background-color: #f4f4f4; font-family: Arial, sans-serif;">
    <div style="width: 100%; background-color: #f4f4f4; padding: 20px 0;">
      <table align="center" border="0" cellpadding="0" cellspacing="0" width="600" style="background-color: white; border-radius: 10px; box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);">
        <tr>
          <td align="center" bgcolor="#001F3F" style="padding: 20px 0; color: white; font-size: 28px; font-weight: bold; border-top-left-radius: 10px; border-top-right-radius: 10px;">
            Password Reset
          </td>
        </tr>
        <tr>
          <td style="padding: 30px; font-size: 16px; color: #333333;">
            <p>Dear <strong>{user.first_name}</strong>,</p>
            <p>We received a request to reset the password for your account. If you made this request, please click the button below to reset your password:</p>

            <p style="text-align: center;">
              <a href="{abslink}" style="
                  background-color: #001F3F;
                  color: white;
                  padding: 15px 25px;
                  text-align: center;
                  text-decoration: none;
                  display: inline-block;
                  font-size: 18px;
                  border-radius: 5px;
                  margin: 20px 0;
                  font-weight: bold;">
                Reset Password
              </a>
            </p>

            <p>If you did not request a password reset, please ignore this email or contact our support team if you have any concerns.</p>

            <p style="color: #888888; font-size: 14px; margin-top: 30px;">For your security, this link will expire in 3 Days.</p>
          </td>
        </tr>
        <tr>
          <td align="center" bgcolor="#f4f4f4" style="padding: 20px; font-size: 14px; color: #555555; border-bottom-left-radius: 10px; border-bottom-right-radius: 10px;">
            <p>Thank you,<br>Noteverse Team</p>
          </td>
        </tr>
      </table>
    </div>
  </body>
</html>
'''

            data = {
                'email_body': email_body,
                'email_subject': "Reset your Password",
                'to_email': user.email
            }
            send_normal_email(data)

        return super().validate(attrs)


class SetNewPasswordSerializer(serializers.Serializer):
    password = serializers.CharField(max_length=100, min_length=8, write_only=True)
    confirm_password = serializers.CharField(max_length=100, min_length=8, write_only=True)
    uidb64 = serializers.CharField(write_only=True)
    token = serializers.CharField(write_only=True)

    class Meta:
        fields = ["password", "confirm_password", "uidb64", "token"]

    def validate(self, attrs):
        password = attrs.get('password')
        confirm_password = attrs.get('confirm_password')

        # ตรวจสอบว่ารหัสผ่านตรงกันหรือไม่
        if password != confirm_password:
            raise AuthenticationFailed("Passwords do not match.")

        # ตรวจสอบความปลอดภัยของรหัสผ่าน
        if len(password) < 8:
            raise serializers.ValidationError('Password must be at least 8 characters long.')
        if not re.search(r'[A-Z]', password):
            raise serializers.ValidationError('Password must contain at least one uppercase letter.')
        if not re.search(r'[a-z]', password):
            raise serializers.ValidationError('Password must contain at least one lowercase letter.')
        if not re.search(r'[0-9]', password):
            raise serializers.ValidationError('Password must contain at least one digit.')
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            raise serializers.ValidationError('Password must contain at least one special character.')

        # ตรวจสอบความถูกต้องของ token และ uid
        try:
            user_id = force_str(urlsafe_base64_decode(attrs.get('uidb64')))
            user = User.objects.get(id=user_id)
            if not PasswordResetTokenGenerator().check_token(user, attrs.get('token')):
                raise AuthenticationFailed("The reset link is invalid or has expired.")
        except Exception:
            raise AuthenticationFailed("The reset link is invalid or has expired.")

        user.set_password(password)
        user.save()

        return user


class LogoutUserSerializer(serializers.Serializer):
    refresh_token = serializers.CharField()

    default_error_messages = {
        'bad_token': ('Token is invalid or has expired')
    }

    def validate(self, attrs):
        self.token = attrs.get('refresh_token')
        return attrs

    def save(self, **kwargs):
        try:
            token = RefreshToken(self.token)
            token.blacklist()
        except TokenError:
            self.fail('bad_token')
            
from rest_framework import serializers
from django.contrib.auth.hashers import check_password
from .models import User

class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)

    def validate_old_password(self, value):
        user = self.context['request'].user
        if not check_password(value, user.password):
            raise serializers.ValidationError("Old password is incorrect.")
        return value

    def validate_new_password(self, value):
        # คุณสามารถเพิ่มเงื่อนไขความปลอดภัยของรหัสผ่านใหม่ที่ต้องการที่นี่
        return value

    def save(self, **kwargs):
        user = self.context['request'].user
        user.set_password(self.validated_data['new_password'])
        user.save()