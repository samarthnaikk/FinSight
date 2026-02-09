"""
Chatbot service for integrating with Backboard.io for stateful conversation.
"""
import os
import asyncio
from typing import List, Dict, Any
from decouple import config


class ChatbotService:
    """
    Service for managing stateful conversations using Backboard.io with Gemini Flash 2.5.
    """
    
    def __init__(self):
        """Initialize the Backboard client."""
        self.backboard_api_key = config("BACKBOARD_API_KEY", default=None)
        self.provider = "google"
        self.model = "gemini-flash-2.5"
        
        if not self.backboard_api_key:
            raise ValueError("BACKBOARD_API_KEY not configured in environment")
        
        # Lazy import to avoid issues if backboard-sdk is not installed
        try:
            from backboard import BackboardClient
            self.client = BackboardClient(api_key=self.backboard_api_key)
        except ImportError:
            raise ImportError("backboard-sdk not installed. Please install it to use the chatbot.")
    
    def get_or_create_thread_id(self, user_id: int) -> str:
        """
        Generate a consistent thread ID for a user.
        In a production system, this would be stored in the database.
        """
        return f"user_{user_id}_thread"
    
    async def generate_response(
        self, 
        user_id: int,
        message: str, 
        conversation_history: List[Dict[str, str]]
    ) -> str:
        """
        Generate a response using Backboard.io with conversation history.
        
        Args:
            user_id: The user's ID
            message: The current user message
            conversation_history: List of previous messages in format [{"role": "user/assistant", "content": "..."}]
        
        Returns:
            The assistant's response
        """
        try:
            # Create an assistant for financial conversations
            assistant = await self.client.create_assistant(
                name="FinSight AI Assistant",
                system_prompt=(
                    "You are FinSight AI, a professional financial assistant. "
                    "You provide clear, accurate, and helpful information about financial topics. "
                    "Always maintain context from the conversation history and provide personalized responses. "
                    "Be concise but thorough, and always prioritize accuracy."
                )
            )
            
            # Get or create thread ID
            thread_id = self.get_or_create_thread_id(user_id)
            
            # Create or reuse thread
            try:
                thread = await self.client.get_thread(thread_id)
            except Exception:
                # Thread doesn't exist, create a new one
                thread = await self.client.create_thread(assistant.assistant_id)
            
            # Build context from conversation history
            context_messages = []
            for msg in conversation_history[-10:]:  # Last 10 messages for context
                role = msg.get("role", "user")
                content = msg.get("content", "")
                if role and content:
                    context_messages.append(f"{role.capitalize()}: {content}")
            
            # Prepare the message with context
            full_message = message
            if context_messages:
                context = "\n".join(context_messages)
                full_message = f"Previous conversation:\n{context}\n\nCurrent message: {message}"
            
            # Send message to Backboard
            response = await self.client.add_message(
                thread_id=thread.thread_id,
                content=full_message,
                llm_provider=self.provider,
                model_name=self.model,
                stream=False
            )
            
            return response.content
            
        except Exception as e:
            raise RuntimeError(f"Backboard API Error: {str(e)}")
    
    def generate_response_sync(
        self, 
        user_id: int,
        message: str, 
        conversation_history: List[Dict[str, str]]
    ) -> str:
        """
        Synchronous wrapper for generate_response.
        Uses asyncio.run() to execute the async function.
        """
        # Use asyncio.run() which properly handles the event loop
        import sys
        if sys.version_info >= (3, 7):
            return asyncio.run(
                self.generate_response(user_id, message, conversation_history)
            )
        else:
            # Fallback for older Python versions
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                return loop.run_until_complete(
                    self.generate_response(user_id, message, conversation_history)
                )
            finally:
                loop.close()


# Singleton instance
_chatbot_service = None

def get_chatbot_service() -> ChatbotService:
    """Get or create the chatbot service singleton."""
    global _chatbot_service
    if _chatbot_service is None:
        _chatbot_service = ChatbotService()
    return _chatbot_service
