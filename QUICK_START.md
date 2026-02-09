# FinSight Quick Start Guide

## 🚀 Get Started in 3 Steps

### Step 1: Start the Services

**Terminal 1 - Backend:**
```bash
cd backend
python manage.py runserver 8000
```

**Terminal 2 - Models:**
```bash
cd models
uvicorn app:app --host 0.0.0.0 --port 8001
```

**Terminal 3 - Frontend:**
```bash
cd frontend
npm run dev
```

### Step 2: Test Connectivity

```bash
./test_integration.sh
```

### Step 3: Access the Application

Open your browser and navigate to:
```
http://localhost:5173
```

## 📝 First Time Usage

1. Click **"GET STARTED"** on the landing page
2. Fill in the registration form
3. Check your email for OTP (or check terminal logs if email not configured)
4. Enter the OTP to verify your email
5. Sign in with your credentials
6. Explore the dashboard and features!

## 🎯 Available Features

Once signed in, you can access:

- **💬 Chatbot** - Chat with the AI assistant
- **🎤 Audio Transcription** - Upload audio files to transcribe
- **📄 Text Processing** - Process transcripts with PII filtering
- **📊 Data Ingestion** - Ingest confidential financial data

## 🔧 Troubleshooting

### Services Not Running?
Make sure all three services are started and running on correct ports.

### CORS Errors?
Verify all services are on their designated ports:
- Frontend: 5173
- Backend: 8000
- Models: 8001

### Authentication Issues?
- Clear localStorage in browser DevTools
- Make sure email is verified with OTP
- Check that JWT token is being stored

## 📚 More Information

- **Full Integration Guide**: See `INTEGRATION_GUIDE.md`
- **API Documentation**: See `documentation.md`
- **Complete Report**: See `COMPLETION_REPORT.md`

## 🔐 Security Note

This integration uses JWT authentication with tokens stored in localStorage.

---

**Need Help?** Check `INTEGRATION_GUIDE.md` for detailed documentation
