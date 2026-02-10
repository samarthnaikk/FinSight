# FinSight Chatbot Setup Guide

## Overview

The FinSight chatbot is a stateful conversational AI powered by Backboard.io and Google's Gemini Flash 2.5 model. It maintains conversation history in an encrypted database and provides contextual responses based on previous interactions.

## Features

- **Stateful Conversations**: Remembers previous messages in the conversation
- **Encrypted Storage**: All conversation history is encrypted in the database
- **Contextual Responses**: Uses conversation history to provide relevant answers
- **Real-time Typing Indicators**: Shows when the AI is generating a response
- **Smooth Animations**: Message send/receive animations for better UX
- **Conversation History Loading**: Automatically loads previous conversations on page load

## Configuration

### Backend Setup

1. **Add Backboard API Key to Environment**

   The chatbot requires a Backboard API key to function. Add the following to your backend `.env` file or environment variables:

   ```
   BACKBOARD_API_KEY=your_backboard_api_key_here
   ```

   You can obtain a Backboard API key from [Backboard.io](https://backboard.io).

2. **Install Dependencies**

   Make sure the backend has the required dependencies installed:

   ```bash
   cd backend
   pip install -r requirements.txt
   ```

   The key dependency is `backboard-sdk` which is now included in `requirements.txt`.

3. **Verify Configuration**

   The chatbot service will automatically validate that the `BACKBOARD_API_KEY` is configured on startup. If it's missing, you'll see an error when trying to use the chatbot.

### Frontend Setup

No additional frontend configuration is required. The chatbot page will automatically:
- Load conversation history when opened
- Display typing indicators during AI response generation
- Show smooth animations for message send/receive

## Usage

1. Navigate to the Chatbot page from the dashboard
2. Type your message in the input field
3. Press "Send" or hit Enter
4. The chatbot will:
   - Display your message immediately
   - Show a typing indicator while processing
   - Return a contextual response based on conversation history
5. All messages are automatically saved and encrypted in the database

## Technical Details

### Model Configuration

- **Provider**: Google
- **Model**: gemini-flash-2.5
- **Context Window**: Last 10 messages are used for context
- **Thread Management**: Each user has a persistent thread ID

### Security

- All conversation messages are encrypted using the application's encryption service
- Messages are stored in the `ChatMemory` model with a one-to-one relationship to users
- Only authenticated users can access their own conversation history

### API Endpoints

**GET /api/chat/message/**
- Retrieves encrypted conversation history for authenticated user
- Returns: `{ success: true, data: { messages: [...] } }`

**POST /api/chat/message/**
- Sends a message and receives AI response
- Request: `{ message: "Your message here" }`
- Returns: `{ success: true, data: { message: "AI response", role: "assistant" } }`

## Troubleshooting

### "BACKBOARD_API_KEY not configured"

**Solution**: Add the `BACKBOARD_API_KEY` to your backend environment variables or `.env` file.

### Chatbot not responding

**Possible causes**:
1. Backend server not running on port 8000
2. Invalid or expired Backboard API key
3. Network connectivity issues

**Solutions**:
- Verify backend is running: `curl http://localhost:8000/api/chat/message/`
- Check backend logs for error messages
- Verify API key is valid

### Conversation history not loading

**Possible causes**:
1. User authentication issue
2. Database connection problem
3. Frontend not connected to backend

**Solutions**:
- Check browser console for errors
- Verify user is authenticated (check localStorage for tokens)
- Ensure backend server is running and accessible

## Architecture

```
Frontend (ChatbotPage.jsx)
    ↓
Backend API (ChatMessageView)
    ↓
Chatbot Service (chatbot_service.py)
    ↓
Backboard SDK
    ↓
Google Gemini Flash 2.5
```

## Development Notes

- The chatbot uses Django's synchronous views with async wrappers for Backboard calls
- Conversation history is limited to the last 10 messages for context to avoid token limits
- Thread IDs are generated based on user IDs for consistency
- Error handling ensures user messages are saved even if AI generation fails

## Future Enhancements

Potential improvements that could be added:
- Conversation reset/clear functionality
- Export conversation history
- Message editing/deletion
- Support for file attachments
- Voice input integration
- Multi-language support

---

For more information, see the main [README.md](README.md) and [QUICK_START.md](QUICK_START.md).
