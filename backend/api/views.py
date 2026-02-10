from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status

from .serializers import AIIngestSerializer, ChatMessageSerializer
from .models import ConfidentialData, NonConfidentialData,ChatMemory
from .utils.encryption import encryption_service
from .chatbot_service import get_chatbot_service



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

    def get(self, request):
        """Get conversation history for the authenticated user."""
        user = request.user
        
        try:
            chat_memory = ChatMemory.objects.get(user=user)
            messages = encryption_service.decrypt(chat_memory.encrypted_messages)
        except ChatMemory.DoesNotExist:
            messages = []
        
        return Response(
            {
                "success": True,
                "data": {
                    "messages": messages,
                },
                "error": None,
            },
            status=status.HTTP_200_OK
        )

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

        # Append new user message
        messages.append({
            "role": "user",
            "content": message,
        })

        # Generate AI response using Backboard with conversation history
        try:
            chatbot_service = get_chatbot_service()
            ai_response = chatbot_service.generate_response_sync(
                user_id=user.id,
                message=message,
                conversation_history=messages
            )
            
            # Append assistant response
            messages.append({
                "role": "assistant",
                "content": ai_response,
            })
            
            # Re-encrypt and save
            chat_memory.encrypted_messages = encryption_service.encrypt(messages)
            chat_memory.save()
            
            return Response(
                {
                    "success": True,
                    "data": {
                        "message": ai_response,
                        "role": "assistant",
                    },
                    "error": None,
                },
                status=status.HTTP_200_OK
            )
            
        except Exception as e:
            # If AI generation fails, still save the user message but return error
            chat_memory.encrypted_messages = encryption_service.encrypt(messages)
            chat_memory.save()
            
            return Response(
                {
                    "success": False,
                    "data": None,
                    "error": f"Failed to generate response: {str(e)}",
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
