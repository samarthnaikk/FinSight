from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status

from .serializers import AIIngestSerializer, ChatMessageSerializer
from .models import ConfidentialData, NonConfidentialData,ChatMemory
from .utils.encryption import encryption_service



class AIIngestView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = AIIngestSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(
                {
                    "success": False,
                    "data": None,
                    "error": serializer.errors,
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        user = request.user
        confidential = serializer.validated_data["confidential"]
        non_confidential = serializer.validated_data["non_confidential"]

        # Encrypt payloads
        encrypted_confidential = encryption_service.encrypt(confidential)
        encrypted_non_confidential = encryption_service.encrypt(non_confidential)

        # Save to DB
        ConfidentialData.objects.create(
            user=user,
            encrypted_payload=encrypted_confidential
        )

        NonConfidentialData.objects.create(
            user=user,
            encrypted_payload=encrypted_non_confidential
        )

        return Response(
            {
                "success": True,
                "data": {
                    "message": "Data ingested successfully"
                },
                "error": None,
            },
            status=status.HTTP_201_CREATED
        )


class ChatMessageView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = ChatMessageSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(
                {
                    "success": False,
                    "data": None,
                    "error": serializer.errors,
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        user = request.user
        message = serializer.validated_data["message"]

        # Fetch or create chat memory
        chat_memory, created = ChatMemory.objects.get_or_create(
            user=user,
            defaults={
                "encrypted_messages": encryption_service.encrypt([])
            }
        )

        # Decrypt existing messages
        messages = encryption_service.decrypt(chat_memory.encrypted_messages)

        # Append new message
        messages.append({
            "role": "user",
            "content": message,
        })

        # Re-encrypt and save
        chat_memory.encrypted_messages = encryption_service.encrypt(messages)
        chat_memory.save()

        return Response(
            {
                "success": True,
                "data": {
                    "message": "Message stored successfully",
                    "memory_length": len(messages),
                },
                "error": None,
            },
            status=status.HTTP_200_OK
        )
