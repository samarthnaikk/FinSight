from rest_framework.views import APIView
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from django.core.mail import send_mail
from django.utils import timezone
from datetime import timedelta

from .utils import generate_otp
from .models import User
from .serializers import RegisterSerializer
from .responses import success_response, error_response


class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)

        if not serializer.is_valid():
            return error_response(
                code="VALIDATION_ERROR",
                message=serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )

        user = serializer.save()

        # 🔐 Generate & send OTP automatically
        otp = generate_otp()
        user.otp = otp
        user.otp_created_at = timezone.now()
        user.save()

        send_mail(
            subject="FinSight AI - Email Verification OTP",
            message=f"Your OTP is {otp}. It is valid for 5 minutes.",
            from_email="no-reply@finsight.ai",
            recipient_list=[user.email],
        )

        return success_response(
            data={
                "message": "User registered successfully. OTP sent to email."
            },
            status=status.HTTP_201_CREATED
        )


class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        identifier = request.data.get("identifier")
        password = request.data.get("password")

        if not identifier or not password:
            return error_response(
                code="MISSING_CREDENTIALS",
                message="Identifier and password are required",
                status=status.HTTP_400_BAD_REQUEST
            )

        user = (
            User.objects.filter(username=identifier).first()
            or User.objects.filter(email=identifier).first()
        )

        if user is None or not user.check_password(password):
            return error_response(
                code="INVALID_CREDENTIALS",
                message="Invalid username/email or password",
                status=status.HTTP_401_UNAUTHORIZED
            )

        if not user.is_email_verified:
            return error_response(
                code="EMAIL_NOT_VERIFIED",
                message="Email not verified",
                status=status.HTTP_403_FORBIDDEN
            )

        refresh = RefreshToken.for_user(user)

        return success_response(
            data={
                "access": str(refresh.access_token),
                "refresh": str(refresh)
            },
            status=status.HTTP_200_OK
        )


class MeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        return success_response(
            data={
                "id": user.id,
                "name": user.name,
                "username": user.username,
                "email": user.email,
            },
            status=status.HTTP_200_OK
        )


class SendOTPView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get("email")

        if not email:
            return error_response(
                code="EMAIL_REQUIRED",
                message="Email is required",
                status=status.HTTP_400_BAD_REQUEST
            )

        user = User.objects.filter(email=email).first()
        if not user:
            return error_response(
                code="USER_NOT_FOUND",
                message="User not found",
                status=status.HTTP_404_NOT_FOUND
            )

        # 🔁 Max resend limit
        if user.otp_resend_count >= 3:
            return error_response(
                code="OTP_RESEND_LIMIT_REACHED",
                message="Maximum OTP resend attempts reached",
                status=status.HTTP_429_TOO_MANY_REQUESTS
            )

        # ⏱ Cooldown check (60 seconds)
        if user.otp_last_sent_at:
            elapsed = timezone.now() - user.otp_last_sent_at
            if elapsed.total_seconds() < 60:
                return error_response(
                    code="OTP_COOLDOWN",
                    message="Please wait before requesting another OTP",
                    status=status.HTTP_429_TOO_MANY_REQUESTS
                )

        otp = generate_otp()
        user.otp = otp
        user.otp_created_at = timezone.now()
        user.otp_last_sent_at = timezone.now()
        user.otp_resend_count += 1
        user.save()

        send_mail(
            subject="FinSight AI - Email Verification OTP",
            message=f"Your OTP is {otp}. It is valid for 5 minutes.",
            from_email="no-reply@finsight.ai",
            recipient_list=[user.email],
        )

        return success_response(
            data={"message": "OTP sent successfully"},
            status=status.HTTP_200_OK
        )


class VerifyOTPView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get("email")
        otp = request.data.get("otp")

        if not email or not otp:
            return error_response(
                code="MISSING_OTP_DATA",
                message="Email and OTP are required",
                status=status.HTTP_400_BAD_REQUEST
            )

        user = User.objects.filter(email=email, otp=otp).first()
        if not user:
            return error_response(
                code="INVALID_OTP",
                message="Invalid OTP",
                status=status.HTTP_400_BAD_REQUEST
            )

        if timezone.now() - user.otp_created_at > timedelta(minutes=5):
            return error_response(
                code="OTP_EXPIRED",
                message="OTP expired",
                status=status.HTTP_400_BAD_REQUEST
            )

        user.is_email_verified = True
        user.otp = None
        user.otp_created_at = None
        user.otp_resend_count = 0
        user.otp_last_sent_at = None
        user.save()

        return success_response(
            data={"message": "Email verified successfully"},
            status=status.HTTP_200_OK
        )


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        refresh_token = request.data.get("refresh")

        if not refresh_token:
            return error_response(
                code="REFRESH_TOKEN_REQUIRED",
                message="Refresh token is required",
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            token = RefreshToken(refresh_token)
            token.blacklist()
        except Exception:
            return error_response(
                code="INVALID_REFRESH_TOKEN",
                message="Invalid or expired refresh token",
                status=status.HTTP_400_BAD_REQUEST
            )

        return success_response(
            data={"message": "Logged out successfully"},
            status=status.HTTP_200_OK
        )
