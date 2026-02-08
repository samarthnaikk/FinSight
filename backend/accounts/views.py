from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated
from .models import User    
from .serializers import RegisterSerializer

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
