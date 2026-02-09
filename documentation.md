# FinSight — Unified Routes and API Endpoints Documentation

This document provides a consolidated reference for **all routes and API endpoints** across the FinSight project. It is organized by folder: **Backend**, **Frontend**, and **Models**.

---

## Table of Contents

1. [Backend](#backend)
   - [Authentication Endpoints (`accounts`)](#authentication-endpoints-accounts)
   - [API Endpoints (`api`)](#api-endpoints-api)
2. [Frontend](#frontend)
   - [Client-Side Routes](#client-side-routes)
3. [Models](#models)
   - [Root Endpoints](#root-endpoints)
   - [Transcription Endpoints (`audiotext`)](#transcription-endpoints-audiotext)
   - [Transcript Processing Endpoints (`filtertext`)](#transcript-processing-endpoints-filtertext)

---

## Backend

The backend is a Django application using Django REST Framework with JWT authentication. All backend routes are defined in `backend/core/urls.py` and delegated to individual app URL configurations.

### URL Routing Overview

| Prefix           | Includes              | Description                       |
| ---------------- | --------------------- | --------------------------------- |
| `api/auth/`      | `accounts.urls`       | Authentication and user management |
| `api/`           | `api.urls`            | AI data ingestion and chat        |

### Authentication Endpoints (`accounts`)

**Base path:** `/api/auth/`

| HTTP Method | Endpoint                   | View Class         | Auth Required | Description                                      |
| ----------- | -------------------------- | ------------------ | ------------- | ------------------------------------------------ |
| POST        | `/api/auth/register/`      | `RegisterView`     | No            | Register a new user account                      |
| POST        | `/api/auth/login/`         | `LoginView`        | No            | Login with username/email and password            |
| GET         | `/api/auth/me/`            | `MeView`           | Yes (JWT)     | Get current authenticated user profile            |
| POST        | `/api/auth/send-otp/`      | `SendOTPView`      | No            | Send OTP to user's email for verification         |
| POST        | `/api/auth/verify-otp/`    | `VerifyOTPView`    | No            | Verify OTP to complete email verification         |
| POST        | `/api/auth/logout/`        | `LogoutView`       | Yes (JWT)     | Logout and blacklist refresh token                |
| POST        | `/api/auth/token/refresh/` | `TokenRefreshView` | No            | Refresh JWT access token using refresh token      |
| POST        | `/api/auth/google/`        | `GoogleAuthView`   | No            | Authenticate with Google OAuth ID token           |

**Source files:**
- `backend/accounts/urls.py`
- `backend/accounts/views.py`

### API Endpoints (`api`)

**Base path:** `/api/`

| HTTP Method | Endpoint              | View Class        | Auth Required | Description                                  |
| ----------- | --------------------- | ----------------- | ------------- | -------------------------------------------- |
| POST        | `/api/ai/ingest/`     | `AIIngestView`    | Yes (JWT)     | Ingest confidential and non-confidential data |
| POST        | `/api/chat/message/`  | `ChatMessageView` | Yes (JWT)     | Store a chat message in encrypted memory      |

**Source files:**
- `backend/api/urls.py`
- `backend/api/views.py`

---

## Frontend

The frontend is a React application using React Router for client-side routing. Routes are defined in `frontend/src/App.jsx`.

### Client-Side Routes

| Path           | Component              | Description                              |
| -------------- | ---------------------- | ---------------------------------------- |
| `/`            | `LandingPage`          | Landing page with hero section and navigation links |
| `/signin`      | `SignInPage`           | User sign-in form                        |
| `/signup`      | `SignUpPage`           | User registration form                   |
| `/verify-otp`  | `OtpVerificationPage`  | OTP verification page for email confirmation |

**Source files:**
- `frontend/src/App.jsx`
- `frontend/src/pages/SignInPage.jsx`
- `frontend/src/pages/SignUpPage.jsx`
- `frontend/src/pages/OtpVerificationPage.jsx`

---

## Models

The models service is a FastAPI application providing audio transcription and transcript post-processing capabilities. The main app is defined in `models/app.py` and mounts two sub-routers.

### Root Endpoints

| HTTP Method | Endpoint   | Description                                       |
| ----------- | ---------- | ------------------------------------------------- |
| GET         | `/`        | Root endpoint returning API information and available endpoints |
| GET         | `/health`  | Health check endpoint returning service status     |

**Source file:** `models/app.py`

### Transcription Endpoints (`audiotext`)

**Prefix:** `/transcribe`

| HTTP Method | Endpoint       | Description                                                        |
| ----------- | -------------- | ------------------------------------------------------------------ |
| POST        | `/transcribe`  | Transcribe an uploaded audio file (`.wav` or `.mp3`) to text using Groq Whisper model |

**Request:** Multipart file upload (`file` field)

**Source files:**
- `models/audiotext/router.py`
- `models/audiotext/service.py`

### Transcript Processing Endpoints (`filtertext`)

**Prefix:** `/filtertext`

| HTTP Method | Endpoint                 | Description                                                              |
| ----------- | ------------------------ | ------------------------------------------------------------------------ |
| POST        | `/filtertext/process`      | Process transcript text through the pipeline (PII removal and structured output generation) |
| POST        | `/filtertext/process-file` | Process an existing transcript file from the transcriptions directory      |
| GET         | `/filtertext/status`       | Get the status and configuration of the transcript processing service     |

**Source files:**
- `models/filtertext/router.py`
- `models/filtertext/service.py`

---

*This documentation reflects the current state of routes and API endpoints in the FinSight codebase. No code was modified in the creation of this file.*
