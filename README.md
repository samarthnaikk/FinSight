# FinSight AI

FinSight AI is an end-to-end financial intelligence platform that transforms unstructured voice calls and complex financial documents into structured, actionable insights. The system leverages advanced speech-to-text, NLP, and multimodal AI to analyze customer support calls, advisory conversations, and earnings discussions, extracting key financial entities, intents, risks, and compliance signals.

## Features

### Core Features
- **Advanced speech-to-text and NLP** for voice call analysis
- **Multimodal AI** for document processing (200+ formats: invoices, bank statements, contracts, loan agreements, reports)
- **Accurate data extraction**, validation, and normalization beyond rule-based OCR
- **Real-time financial decision support** for enterprises
- **AI-powered chatbot** for financial insights and analysis
- **PII filtering and data security** with field-level encryption

### Authentication
- **Email/Password Authentication** with OTP verification
- **Google OAuth Sign-In** for seamless authentication
- JWT-based secure token management

### User Interface
- **Modern, responsive dashboard** with 2x2 feature grid layout
- **Copy-to-clipboard functionality** for transcriptions and processed data
- **Animated SVG components** for enhanced user experience
- **Dark theme** with silver and gold accents

## Tech Stack

### Backend
- **Python** with Django REST Framework
- **FastAPI** for models service
- **PostgreSQL** for production database
- **JWT** for authentication
- **Google OAuth 2.0** for social login
- **Cryptography** for field-level encryption

### Frontend
- **React 18** with Vite
- **React Router** for navigation
- **@react-oauth/google** for Google Sign-In
- **React Markdown** for rich text rendering

### AI/ML Services
- **Groq API** for audio transcription (Whisper)
- **Backboard.io** for stateful conversations and structured output
- **Google OAuth** for authentication

### Infrastructure
- **Docker** and Docker Compose for containerization
- **CORS** support for cross-origin requests

## Getting Started

### Prerequisites
- Python 3.8+ (backend)
- Node.js 16+ (frontend)
- Docker and Docker Compose (optional)
- PostgreSQL (for production)

### Environment Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/samarthnaikk/FinSight.git
   cd FinSight
   ```

2. **Configure environment variables**
   
   Copy `.env.example` to `.env` and configure:
   
   ```bash
   cp .env.example .env
   ```

   **Required variables:**
   - `DJANGO_SECRET_KEY` - Django secret key
   - `BACKBOARD_API_KEY` - For chatbot and text processing
   - `GROQ_API_KEY` - For audio transcription
   - `GOOGLE_CLIENT_ID` - For Google OAuth (both backend and frontend)
   - `FIELD_ENCRYPTION_KEY` - For data encryption

   **Frontend environment:**
   Create `frontend/.env.local`:
   ```
   VITE_GOOGLE_CLIENT_ID=your_google_client_id_here
   ```

### Installation

#### Backend Setup
```bash
cd backend
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

#### Frontend Setup
```bash
cd frontend
npm install
npm run dev
```

#### Models Service Setup
```bash
cd models
pip install -r requirements.txt
uvicorn main:app --reload --port 8001
```

### Docker Setup

For a complete Docker-based setup, see [DOCKER_SETUP.md](DOCKER_SETUP.md)

```bash
docker-compose up --build
```

## Google OAuth Setup

### 1. Create Google OAuth Credentials

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing one
3. Enable **Google+ API**
4. Go to **Credentials** → **Create Credentials** → **OAuth 2.0 Client ID**
5. Configure consent screen
6. Add authorized JavaScript origins:
   - `http://localhost:5173` (frontend dev)
   - `http://localhost:3000` (alternative)
   - Your production domain
7. Copy the **Client ID**

### 2. Configure Backend
Add to `backend/.env`:
```
GOOGLE_CLIENT_ID=your_client_id_here.apps.googleusercontent.com
```

### 3. Configure Frontend
Add to `frontend/.env.local`:
```
VITE_GOOGLE_CLIENT_ID=your_client_id_here.apps.googleusercontent.com
```

### 4. Test Google Sign-In
1. Start backend: `python manage.py runserver`
2. Start frontend: `npm run dev`
3. Navigate to Sign In page
4. Click "Sign in with Google" button
5. Complete Google authentication flow

## API Integration

- **Backboard.io APIs** for workflow automation and analytics
- **Groq Whisper API** for audio transcription
- **Google OAuth API** for authentication

## Features Guide

### Chatbot
- Stateful conversations with financial domain expertise
- Context-aware responses using conversation history
- Markdown formatting for structured output
- **Fixed:** Alternate message error resolved with proper thread caching

### Audio Transcription
- Upload audio files (.wav, .mp3)
- AI-powered transcription using Whisper
- Copy transcription to clipboard with one click
- Animated "Drop Your Audio" interface

### Text Processing
- Process transcripts with PII filtering
- Generate structured financial data
- Copy processed output to clipboard
- JSON-formatted structured data

### Dashboard
- 2x2 grid layout for quick feature access
- Responsive design (mobile-friendly)
- Modern animations and transitions
- Finance-themed logo with visual enhancements

## Security Features

- **JWT-based authentication** with access and refresh tokens
- **Field-level encryption** for sensitive chat data
- **PII filtering** in text processing pipeline
- **Google OAuth** for secure third-party authentication
- **CORS protection** with configurable origins

## Documentation

- [Quick Start Guide](QUICK_START.md)
- [Docker Setup](DOCKER_SETUP.md)
- [Integration Guide](INTEGRATION_GUIDE.md)
- [Chatbot Setup](CHATBOT_SETUP.md)
- [UI Improvements](UI_IMPROVEMENTS.md)

## Recent Updates

### Latest Changes
- ✅ **Google OAuth Integration** - Sign in with Google now available
- ✅ **Chatbot Bug Fix** - Resolved alternate message error with proper thread management
- ✅ **Copy Buttons** - Added SVG-based copy functionality for outputs
- ✅ **Dashboard Redesign** - 2x2 grid layout with responsive design
- ✅ **Visual Enhancements** - Finance logo and animated SVG components
- ✅ **UI Polish** - Improved spacing, alignment, and animations

## License

MIT License

## Contact

For inquiries, reach out to the project maintainers or open an issue on GitHub.

## Contributing

Contributions are welcome! Please read our contributing guidelines and submit pull requests for any enhancements.
