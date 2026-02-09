# FinSight Backend API Documentation

**Generated:** February 9, 2026  
**Version:** 1.0  
**Framework:** Django 6.0.2 with Django REST Framework

---

## Table of Contents

1. [Overview](#overview)
2. [API Routes & Endpoints](#api-routes--endpoints)
3. [Models](#models)
4. [Views & Endpoints Detail](#views--endpoints-detail)
5. [Serializers](#serializers)
6. [Utility Functions](#utility-functions)
7. [Configuration](#configuration)
8. [Authentication](#authentication)

---

## Overview

FinSight is a Django-based REST API backend that provides user authentication, email verification via OTP, and JWT-based token management. The backend is organized into modular Django apps:

- **`core`**: Main project configuration and routing
- **`accounts`**: User authentication, registration, and OTP verification
- **`api`**: Placeholder app for future API endpoints

---

## API Routes & Endpoints

### Base URL Structure

All authentication routes are prefixed with `/api/auth/`

### Complete Endpoint List

| HTTP Method | Endpoint Path              | View Class         | Authentication Required | Description                                  |
| ----------- | -------------------------- | ------------------ | ----------------------- | -------------------------------------------- |
| **POST**    | `/api/auth/register/`      | `RegisterView`     | No                      | Register a new user account                  |
| **POST**    | `/api/auth/login/`         | `LoginView`        | No                      | Login with username/email and password       |
| **GET**     | `/api/auth/me/`            | `MeView`           | Yes (JWT)               | Get current authenticated user profile       |
| **POST**    | `/api/auth/send-otp/`      | `SendOTPView`      | No                      | Send OTP to user's email for verification    |
| **POST**    | `/api/auth/verify-otp/`    | `VerifyOTPView`    | No                      | Verify OTP to activate email verification    |
| **POST**    | `/api/auth/logout/`        | `LogoutView`       | Yes (JWT)               | Logout and blacklist refresh token           |
| **POST**    | `/api/auth/token/refresh/` | `TokenRefreshView` | No                      | Refresh JWT access token using refresh token |
| **POST**    | `/api/auth/google/`        | `GoogleAuthView`   | No                      | Authenticate with Google OAuth token         |

---

## Models

### `User` Model

**Location:** `backend/accounts/models.py`

Custom user model extending Django's `AbstractBaseUser` and `PermissionsMixin`.

#### Fields

| Field Name          | Type          | Properties                          | Description                      |
| ------------------- | ------------- | ----------------------------------- | -------------------------------- |
| `name`              | CharField     | max_length=100                      | User's full name                 |
| `username`          | CharField     | max_length=50, unique=True          | Unique username for login        |
| `email`             | EmailField    | -                                   | User's email address             |
| `is_email_verified` | BooleanField  | default=False                       | Email verification status        |
| `otp`               | CharField     | max_length=6, blank=True, null=True | Current OTP for verification     |
| `otp_created_at`    | DateTimeField | blank=True, null=True               | Timestamp when OTP was generated |
| `is_active`         | BooleanField  | default=True                        | Account active status            |
| `is_staff`          | BooleanField  | default=False                       | Staff/admin status               |
| `created_at`        | DateTimeField | auto_now_add=True                   | Account creation timestamp       |

#### Configuration

- **USERNAME_FIELD:** `username`
- **REQUIRED_FIELDS:** `["email"]`
- **Manager:** `UserManager`

#### Methods

- `__str__(self)` → Returns the username as string representation

### `UserManager` Class

**Location:** `backend/accounts/models.py`

Custom manager for the User model.

#### Methods

##### `create_user(username, email, password=None, **extra_fields)`

**Purpose:** Creates and saves a regular user with hashed password

**Parameters:**

- `username` (str, required): Unique username
- `email` (str, required): User's email address
- `password` (str, optional): Plain text password (will be hashed)
- `**extra_fields`: Additional user fields

**Returns:** User instance

**Raises:**

- `ValueError`: If username or email is not provided

##### `create_superuser(username, email, password=None, **extra_fields)`

**Purpose:** Creates and saves a superuser with staff and superuser privileges

**Parameters:**

- `username` (str, required): Unique username
- `email` (str, required): User's email address
- `password` (str, optional): Plain text password (will be hashed)
- `**extra_fields`: Additional user fields

**Returns:** User instance with `is_staff=True` and `is_superuser=True`

---

## Views & Endpoints Detail

### `RegisterView`

**Location:** `backend/accounts/views.py`  
**Base Class:** `APIView`  
**Permission:** `AllowAny` (public access)

#### POST `/api/auth/register/`

**Purpose:** Register a new user account

**Request Body:**

```json
{
  "name": "string (required)",
  "username": "string (required, unique)",
  "email": "string (required)",
  "password": "string (required)"
}
```

**Success Response (201 CREATED):**

```json
{
  "success": true,
  "message": "User registered successfully"
}
```

**Error Response (400 BAD REQUEST):**

```json
{
  "field_name": ["error message"]
}
```

**Implementation Details:**

- Uses `RegisterSerializer` for validation and user creation
- Password is automatically hashed during creation
- Email verification is NOT required at registration

---

### `LoginView`

**Location:** `backend/accounts/views.py`  
**Base Class:** `APIView`  
**Permission:** `AllowAny` (public access)

#### POST `/api/auth/login/`

**Purpose:** Authenticate user and return JWT tokens

**Request Body:**

```json
{
  "identifier": "string (username or email)",
  "password": "string"
}
```

**Success Response (200 OK):**

```json
{
  "access": "eyJhbGc...",
  "refresh": "eyJhbGc..."
}
```

**Error Responses:**

**400 BAD REQUEST:**

```json
{
  "error": "Identifier and password are required"
}
```

**401 UNAUTHORIZED:**

```json
{
  "error": "Invalid username/email or password"
}
```

**403 FORBIDDEN:**

```json
{
  "error": "Email not verified"
}
```

**Implementation Details:**

- Accepts either username or email as identifier
- Checks password using Django's `check_password()` method
- Validates email verification status before issuing tokens
- Returns both access and refresh JWT tokens

---

### `MeView`

**Location:** `backend/accounts/views.py`  
**Base Class:** `APIView`  
**Permission:** `IsAuthenticated` (requires JWT token)

#### GET `/api/auth/me/`

**Purpose:** Retrieve current authenticated user's profile information

**Request Headers:**

```
Authorization: Bearer <access_token>
```

**Success Response (200 OK):**

```json
{
  "id": 1,
  "name": "John Doe",
  "username": "johndoe",
  "email": "john@example.com"
}
```

**Error Response (401 UNAUTHORIZED):**

```json
{
  "detail": "Authentication credentials were not provided."
}
```

**Implementation Details:**

- Extracts user from `request.user` (populated by JWT authentication)
- Returns user ID, name, username, and email
- Does not expose sensitive fields like password or OTP

---

### `SendOTPView`

**Location:** `backend/accounts/views.py`  
**Base Class:** `APIView`  
**Permission:** `AllowAny` (public access)

#### POST `/api/auth/send-otp/`

**Purpose:** Generate and send a 6-digit OTP to user's email for verification

**Request Body:**

```json
{
  "email": "string (required)"
}
```

**Success Response (200 OK):**

```json
{
  "success": true,
  "message": "OTP sent successfully"
}
```

**Error Responses:**

**400 BAD REQUEST:**

```json
{
  "error": "Email is required"
}
```

**404 NOT FOUND:**

```json
{
  "error": "User not found"
}
```

**Implementation Details:**

- Generates a 6-digit random OTP using `generate_otp()` utility
- Stores OTP and creation timestamp in user record
- Sends email via Django's `send_mail()` with:
  - Subject: "FinSight AI - Email Verification OTP"
  - Message: "Your OTP is {otp}. It is valid for 5 minutes."
  - From: "no-reply@finsight.ai"
- OTP is valid for 5 minutes

---

### `VerifyOTPView`

**Location:** `backend/accounts/views.py`  
**Base Class:** `APIView`  
**Permission:** `AllowAny` (public access)

#### POST `/api/auth/verify-otp/`

**Purpose:** Verify user's email using the OTP sent via email

**Request Body:**

```json
{
  "email": "string (required)",
  "otp": "string (required, 6 digits)"
}
```

**Success Response (200 OK):**

```json
{
  "success": true,
  "message": "Email verified successfully"
}
```

**Error Responses:**

**400 BAD REQUEST (missing fields):**

```json
{
  "error": "Email and OTP are required"
}
```

**400 BAD REQUEST (invalid OTP):**

```json
{
  "error": "Invalid OTP"
}
```

**400 BAD REQUEST (expired OTP):**

```json
{
  "error": "OTP expired"
}
```

**Implementation Details:**

- Validates OTP matches the one stored in user record
- Checks OTP expiration (5 minutes from creation)
- Sets `is_email_verified = True` on success
- Clears OTP and OTP creation timestamp after verification
- Users can login only after email is verified

---

### `LogoutView`

**Location:** `backend/accounts/views.py`  
**Base Class:** `APIView`  
**Permission:** `IsAuthenticated` (requires JWT token)

#### POST `/api/auth/logout/`

**Purpose:** Logout user by blacklisting their refresh token

**Request Headers:**

```
Authorization: Bearer <access_token>
```

**Request Body:**

```json
{
  "refresh": "string (required, refresh token)"
}
```

**Success Response (200 OK):**

```json
{
  "success": true,
  "message": "Logged out successfully"
}
```

**Error Responses:**

**400 BAD REQUEST (missing token):**

```json
{
  "error": "Refresh token is required"
}
```

**400 BAD REQUEST (invalid token):**

```json
{
  "error": "Invalid or expired refresh token"
}
```

**Implementation Details:**

- Uses `rest_framework_simplejwt.token_blacklist` to blacklist tokens
- Prevents reuse of the refresh token after logout
- Requires both access token (in header) and refresh token (in body)

---

### `TokenRefreshView`

**Location:** `rest_framework_simplejwt.views` (third-party)  
**Base Class:** `TokenRefreshView`  
**Permission:** `AllowAny`

#### POST `/api/auth/token/refresh/`

**Purpose:** Obtain a new access token using a valid refresh token

**Request Body:**

```json
{
  "refresh": "string (required, refresh token)"
}
```

**Success Response (200 OK):**

```json
{
  "access": "eyJhbGc..."
}
```

**Error Response (401 UNAUTHORIZED):**

```json
{
  "detail": "Token is invalid or expired",
  "code": "token_not_valid"
}
```

**Implementation Details:**

- Provided by `djangorestframework-simplejwt` library
- Validates refresh token and issues new access token
- Does not issue a new refresh token (single refresh token lifecycle)

---

### `GoogleAuthView`

**Location:** `backend/accounts/views.py`  
**Base Class:** `APIView`  
**Permission:** `AllowAny` (public access)

#### POST `/api/auth/google/`

**Purpose:** Authenticate user using Google OAuth token and return JWT tokens

**Request Body:**

```json
{
  "token": "string (required, Google OAuth ID token)"
}
```

**Success Response (200 OK):**

```json
{
  "access": "eyJhbGc...",
  "refresh": "eyJhbGc..."
}
```

**Error Responses:**

**400 BAD REQUEST:**

```json
{
  "error": "Token is required"
}
```

**401 UNAUTHORIZED:**

```json
{
  "error": "Invalid token"
}
```

**Implementation Details:**

- Verifies Google OAuth ID token using `google.oauth2.id_token`
- Extracts user information (email, name) from verified token
- Creates new user if email doesn't exist, or retrieves existing user
- Automatically sets `is_email_verified=True` for Google-authenticated users
- Returns both access and refresh JWT tokens
- Requires valid Google OAuth Client ID configured in settings

---

## Serializers

### `RegisterSerializer`

**Location:** `backend/accounts/serializers.py`  
**Base Class:** `serializers.ModelSerializer`

**Purpose:** Validate and create new user accounts

**Model:** `User`

**Fields:**

- `name` (CharField)
- `username` (CharField)
- `email` (EmailField)
- `password` (CharField, write-only)

**Extra Configuration:**

```python
extra_kwargs = {
    "password": {"write_only": True}
}
```

#### Methods

##### `create(validated_data)`

**Purpose:** Create a new user with hashed password

**Parameters:**

- `validated_data` (dict): Validated user data

**Returns:** User instance

**Implementation:**

- Calls `User.objects.create_user()` to ensure password is hashed
- Extracts username, email, password, and name from validated data

---

## Utility Functions

### `generate_otp()`

**Location:** `backend/accounts/utils.py`

**Purpose:** Generate a random 6-digit OTP for email verification

**Parameters:** None

**Returns:** `str` - 6-digit numeric string (e.g., "123456")

**Implementation:**

```python
return str(random.randint(100000, 999999))
```

**Usage:** Called by `SendOTPView` to create verification codes

---

## Configuration

### Django Settings

**Location:** `backend/core/settings.py`

#### Installed Apps

- `django.contrib.admin`
- `django.contrib.auth`
- `django.contrib.contenttypes`
- `django.contrib.sessions`
- `django.contrib.messages`
- `django.contrib.staticfiles`
- `rest_framework`
- `corsheaders`
- `rest_framework_simplejwt.token_blacklist`
- `accounts`

#### Database

- **Engine:** SQLite3
- **Location:** `backend/db.sqlite3`

#### Email Configuration

- **Backend:** `django.core.mail.backends.smtp.EmailBackend`
- **Host:** `smtp.gmail.com`
- **Port:** `465`
- **SSL:** `True`
- **TLS:** `False`
- **From Email:** `FinSight AI <oracleredbullracing.devsoc@gmail.com>`

#### CORS Settings

- **CORS_ALLOW_ALL_ORIGINS:** `True`

#### Custom User Model

- **AUTH_USER_MODEL:** `accounts.User`

---

## Authentication

### JWT Configuration

**Location:** `backend/core/settings.py`

#### REST Framework Settings

```python
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ),
}
```

#### JWT Token Settings

```python
SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=15),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=1),
    "AUTH_HEADER_TYPES": ("Bearer",),
}
```

**Token Lifetime:**

- **Access Token:** 15 minutes
- **Refresh Token:** 1 day

**Header Format:**

```
Authorization: Bearer <access_token>
```

### Authentication Flow

1. **Registration:**
   - User registers with name, username, email, and password
   - Account created but email NOT verified (`is_email_verified=False`)

2. **Email Verification:**
   - User requests OTP via `/api/auth/send-otp/`
   - OTP sent to registered email (valid for 5 minutes)
   - User submits OTP via `/api/auth/verify-otp/`
   - Email verified (`is_email_verified=True`)

3. **Login:**
   - User submits username/email and password
   - System checks credentials and email verification status
   - Returns access and refresh tokens if successful

4. **Authenticated Requests:**
   - Client includes access token in `Authorization` header
   - Access token valid for 15 minutes

5. **Token Refresh:**
   - Client submits refresh token to `/api/auth/token/refresh/`
   - Receives new access token (refresh token valid for 1 day)

6. **Logout:**
   - Client submits refresh token to `/api/auth/logout/`
   - Refresh token blacklisted and cannot be reused

---

## Application Configuration Files

### WSGI Application

**Location:** `backend/core/wsgi.py`

**Purpose:** WSGI callable for production deployment

**Exposed Variable:** `application` (WSGI callable)

**Environment Variable:** `DJANGO_SETTINGS_MODULE=core.settings`

---

### ASGI Application

**Location:** `backend/core/asgi.py`

**Purpose:** ASGI callable for asynchronous deployment

**Exposed Variable:** `application` (ASGI callable)

**Environment Variable:** `DJANGO_SETTINGS_MODULE=core.settings`

---

## App Configurations

### Accounts App

**Location:** `backend/accounts/apps.py`

**Class:** `AccountsConfig`  
**Name:** `accounts`

---

### API App

**Location:** `backend/api/apps.py`

**Class:** `ApiConfig`  
**Name:** `api`

**Status:** Placeholder app with no models or views currently defined

---

## URL Routing Structure

### Root URLs

**Location:** `backend/core/urls.py`

```python
urlpatterns = [
    path("api/auth/", include("accounts.urls")),
]
```

**Note:** Django admin is not currently exposed in URL configuration

---

### Accounts URLs

**Location:** `backend/accounts/urls.py`

All routes under `/api/auth/` prefix:

```python
urlpatterns = [
    path("register/", RegisterView.as_view(), name="register"),
    path("login/", LoginView.as_view(), name="login"),
    path("me/", MeView.as_view(), name="me"),
    path("send-otp/", SendOTPView.as_view()),
    path("verify-otp/", VerifyOTPView.as_view()),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("google/", GoogleAuthView.as_view(), name="google-auth"),
]
```

---

## Dependencies

**Location:** `backend/requirements.txt`

- `django`
- `djangorestframework`
- `django-cors-headers`
- `djangorestframework-simplejwt`
- `python-decouple`
- `requests`
- `google-auth`
- `google-auth-oauthlib`

---

## Notes and Considerations

1. **Email Verification Required:** Users cannot login until their email is verified via OTP
2. **OTP Expiration:** OTPs are valid for 5 minutes only
3. **Token Expiration:** Access tokens expire after 15 minutes; refresh tokens after 1 day
4. **Security:** Passwords are hashed using Django's default password hasher
5. **CORS:** Currently allows all origins (should be restricted in production)
6. **Database:** Using SQLite for development (consider PostgreSQL for production)
7. **Email:** Using Gmail SMTP (credentials exposed in settings.py - move to environment variables)
8. **Admin Panel:** Not currently configured in URLs

---

**End of Documentation**
