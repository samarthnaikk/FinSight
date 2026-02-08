from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated
from django.core.mail import send_mail
from django.utils import timezone
from datetime import timedelta
from .utils import generate_otp
from .models import User    
from .serializers import RegisterSerializer

class VerifyOTPView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get("email")
        otp = request.data.get("otp")

        if not email or not otp:
            return Response(
                {"error": "Email and OTP are required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        user = User.objects.filter(email=email, otp=otp).first()
        if not user:
            return Response(
                {"error": "Invalid OTP"},
                status=status.HTTP_400_BAD_REQUEST
            )

        if timezone.now() - user.otp_created_at > timedelta(minutes=5):
            return Response(
                {"error": "OTP expired"},
                status=status.HTTP_400_BAD_REQUEST
            )

        user.is_email_verified = True
        user.otp = None
        user.otp_created_at = None
        user.save()

        return Response(
            {"success": True, "message": "Email verified successfully"},
            status=status.HTTP_200_OK
        )

class SendOTPView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get("email")

        if not email:
            return Response(
                {"error": "Email is required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        user = User.objects.filter(email=email).first()
        if not user:
            return Response(
                {"error": "User not found"},
                status=status.HTTP_404_NOT_FOUND
            )

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

        return Response(
            {"success": True, "message": "OTP sent successfully"},
            status=status.HTTP_200_OK
        )

class MeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        return Response({
            "id": user.id,
            "name": user.name,
            "username": user.username,
            "email": user.email,
        })
        
class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        identifier = request.data.get("identifier")
        password = request.data.get("password")

        if not identifier or not password:
            return Response(
                {"error": "Identifier and password are required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        user = (
            User.objects.filter(username=identifier).first()
            or User.objects.filter(email=identifier).first()
        )

        if user is None or not user.check_password(password):
            return Response(
                {"error": "Invalid username/email or password"},
                status=status.HTTP_401_UNAUTHORIZED
            )

        if not user.is_email_verified:
            return Response(
                {"error": "Email not verified"},
                status=status.HTTP_403_FORBIDDEN
            )

        refresh = RefreshToken.for_user(user)

        return Response(
            {
                "access": str(refresh.access_token),
                "refresh": str(refresh),
            },
            status=status.HTTP_200_OK
        )
class RegisterView(APIView):
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"success": True, "message": "User registered successfully"},
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
