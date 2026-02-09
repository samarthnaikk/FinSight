# FinSight Frontend-Backend-Models Integration Guide

This document describes the integration between the Frontend, Backend, and Models services in the FinSight application.

## Architecture Overview

The FinSight application consists of three main services:

1. **Frontend** (React + Vite) - Runs on port `5173`
2. **Backend** (Django REST Framework) - Runs on port `8000`
3. **Models** (FastAPI) - Runs on port `8001`

## Service Communication

### Frontend ↔ Backend

The frontend communicates with the backend via REST APIs for:
- User authentication (register, login, OTP verification)
- Chat message storage
- Data ingestion

**Base URL:** `http://localhost:8000`

### Frontend ↔ Models

The frontend communicates directly with the models service for:
- Audio transcription
- Text processing (PII filtering and structured output)

**Base URL:** `http://localhost:8001`

## API Integration

### Authentication Flow

1. **Sign Up** (`POST /api/auth/register/`)
   - Registers a new user
   - Automatically sends OTP to user's email
   
2. **OTP Verification** (`POST /api/auth/verify-otp/`)
   - Verifies the OTP sent to user's email
   - Marks email as verified

3. **Sign In** (`POST /api/auth/login/`)
   - Authenticates user with email/username and password
   - Returns JWT access and refresh tokens
   - Requires verified email

4. **Get User Profile** (`GET /api/auth/me/`)
   - Retrieves current user information
   - Requires JWT authentication

### Feature Integrations

#### 1. Chatbot (`POST /api/chat/message/`)
- Stores user messages in encrypted format
- Requires JWT authentication
- Located at: `/chatbot` route

#### 2. Audio Transcription (`POST /transcribe`)
- Transcribes audio files (.wav, .mp3) to text
- Communicates with Models service (port 8001)
- Located at: `/transcribe` route

#### 3. Text Processing (`POST /filtertext/process`)
- Processes transcript text through PII filtering pipeline
- Generates structured output
- Communicates with Models service (port 8001)
- Located at: `/process-text` route

#### 4. Data Ingestion (`POST /api/ai/ingest/`)
- Ingests confidential and non-confidential data
- Stores data in encrypted format
- Requires JWT authentication
- Located at: `/data-ingest` route

## API Client

The frontend uses a centralized API client (`/frontend/src/utils/api.js`) that provides:
- `backendAPI` - Functions for backend communication
- `modelsAPI` - Functions for models service communication

### Authentication Management

JWT tokens are managed through:
- `AuthContext` - Provides authentication state and functions
- `localStorage` - Stores access and refresh tokens
- Protected routes use `ProtectedRoute` component

## Running the Application

### Prerequisites

Ensure all three services are running:

1. **Backend Server** (Port 8000)
   ```bash
   cd backend
   python manage.py runserver 8000
   ```

2. **Models Server** (Port 8001)
   ```bash
   cd models
   python -m uvicorn app:app --host 0.0.0.0 --port 8001
   ```

3. **Frontend Server** (Port 5173)
   ```bash
   cd frontend
   npm run dev
   ```

### Access Points

- Landing Page: `http://localhost:5173/`
- Sign In: `http://localhost:5173/signin`
- Sign Up: `http://localhost:5173/signup`
- Dashboard: `http://localhost:5173/dashboard` (requires authentication)

## Routes

### Public Routes
- `/` - Landing page
- `/signin` - Sign in page
- `/signup` - Sign up page
- `/verify-otp` - OTP verification page

### Protected Routes (Require Authentication)
- `/dashboard` - Main dashboard with feature access
- `/chatbot` - AI chatbot interface
- `/transcribe` - Audio transcription interface
- `/process-text` - Text processing interface
- `/data-ingest` - Data ingestion interface

## API Response Format

### Backend Responses

All backend endpoints return responses in this format:

**Success:**
```json
{
  "success": true,
  "data": { /* response data */ },
  "error": null
}
```

**Error:**
```json
{
  "success": false,
  "data": null,
  "error": {
    "code": "ERROR_CODE",
    "message": "Error description"
  }
}
```

### Models Service Responses

Models endpoints return direct JSON responses without the success wrapper.

## CORS Configuration

- Backend has CORS enabled for all origins (`CORS_ALLOW_ALL_ORIGINS = True`)
- Models service allows origins from environment variable `ALLOWED_ORIGINS`

## Environment Variables

### Backend
- `DJANGO_SECRET_KEY` - Django secret key
- `DJANGO_DEBUG` - Debug mode
- `GOOGLE_CLIENT_ID` - Google OAuth client ID
- `FIELD_ENCRYPTION_KEY` - Encryption key for sensitive data

### Models
- `GROQ_API_KEY` - Groq API key for transcription
- `BACKBOARD_API_KEY` - Backboard API key for text processing
- `ALLOWED_ORIGINS` - Allowed CORS origins

## Security

- JWT tokens are used for authentication
- Sensitive data is encrypted before storage
- Protected routes require valid JWT tokens
- Tokens are stored in localStorage
- Email verification is required before login

## Testing Integration

You can test the integration using `curl`:

### Test Backend Health
```bash
curl http://localhost:8000/api/auth/me/
```

### Test Models Health
```bash
curl http://localhost:8001/health
```

### Test Frontend
Navigate to `http://localhost:5173` in your browser.

## Troubleshooting

1. **CORS Errors**: Ensure all services are running on their designated ports
2. **Authentication Errors**: Check that JWT tokens are valid and not expired
3. **Connection Refused**: Verify that all services are running
4. **OTP Not Received**: Check email configuration in Django settings

## Future Enhancements

- Add real-time chat using WebSockets
- Implement token refresh mechanism
- Add file upload progress indicators
- Enhance error handling and user feedback
- Add comprehensive testing suite
