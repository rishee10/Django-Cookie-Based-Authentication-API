from django.shortcuts import render

# Create your views here.
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
# from rest_framework.authtoken.models import Token
from rest_framework import status
from django.conf import settings
from django.contrib.auth import authenticate
from rest_framework.authtoken.models import Token

from .models import User, OTP
from .serializers import RegisterSerializer, VerifyOTPSerializer, LoginSerializer, UserDetailSerializer
from .utils import send_otp_email


def set_auth_cookie(response, token_key):
    response.set_cookie(
        key=settings.AUTH_COOKIE_NAME,
        value=token_key,
        httponly=settings.AUTH_COOKIE_HTTPONLY,
        secure=settings.AUTH_COOKIE_SECURE,
        samesite=settings.AUTH_COOKIE_SAMESITE,
    )


class RegisterView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            send_otp_email(user)
            return Response(
                {"message": "OTP sent to your email. Please verify to complete registration."},
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class VerifyOTPView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []

    def post(self, request):
        serializer = VerifyOTPSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        email = serializer.validated_data['email']
        code  = serializer.validated_data['otp']

        try:
            user = User.objects.get(email=email, is_active=False)
            otp  = user.otp
        except (User.DoesNotExist, OTP.DoesNotExist):
            return Response({"error": "No pending registration found for this email."}, status=400)

        if otp.is_expired():
            return Response({"error": "OTP has expired. Please register again."}, status=400)

        if otp.code != code:
            return Response({"error": "Invalid OTP."}, status=400)

        user.is_active = True
        user.save()
        otp.delete()

        return Response({"message": "Email verified. You can now log in."}, status=200)


class LoginView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=400)

        user = authenticate(
            request,
            username=serializer.validated_data['email'],
            password=serializer.validated_data['password']
        )

        if not user:
            return Response({"error": "Invalid credentials."}, status=401)

        if not user.is_active:
            return Response({"error": "Account not verified. Please verify your email."}, status=403)

        token, _ = Token.objects.get_or_create(user=user)
        response = Response({"message": "Login successful."}, status=200)
        set_auth_cookie(response, token.key)
        return response


class MeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = UserDetailSerializer(request.user)
        return Response(serializer.data)


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        # Delete the token from DB
        Token.objects.filter(user=request.user).delete()
        response = Response({"message": "Logged out successfully."}, status=200)
        response.delete_cookie(settings.AUTH_COOKIE_NAME)
        return response