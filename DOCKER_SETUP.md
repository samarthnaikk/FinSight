# Docker Setup for FinSight

This document describes how to run FinSight using Docker Compose.

## Prerequisites

- Docker (version 20.10 or higher)
- Docker Compose (version 2.0 or higher)

## Quick Start

### 1. Configure Environment Variables (Optional)

Copy the example environment file and customize it:

```bash
cp .env.example .env
```

Edit `.env` and fill in your configuration values. **All environment variables are optional** - services will use default values if not provided.

### 2. Build and Start Services

Build and start all services using Docker Compose:

```bash
docker compose build
docker compose up -d
```

The following services will start:
- **PostgreSQL Database**: Port 5432
- **Backend (Django)**: Port 8000
- **Models (FastAPI)**: Port 8001
- **Frontend (React/Vite)**: Port 5173

### 3. Initialize Database

After the services are running, initialize the Django database:

```bash
docker compose exec backend python manage.py migrate
```

### 4. Create a Superuser (Optional)

To access the Django admin panel:

```bash
docker compose exec backend python manage.py createsuperuser
```

### 5. Access the Application

Open your browser and navigate to:
- **Frontend**: http://localhost:5173
- **Backend API**: http://localhost:8000
- **Models API**: http://localhost:8001
- **API Documentation**: http://localhost:8001/docs

## Environment Variables

All environment variables are **optional**. If not provided, services will use default values.

### Backend Configuration

| Variable | Description | Default |
|----------|-------------|---------|
| `DJANGO_SECRET_KEY` | Django secret key for cryptographic signing | `django-insecure-change-this-in-production` |
| `DJANGO_DEBUG` | Enable Django debug mode | `True` |
| `EMAIL_HOST_USER` | Email address for sending OTP emails | *(empty - email disabled)* |
| `EMAIL_HOST_PASSWORD` | Email password | *(empty - email disabled)* |
| `JWT_ACCESS_MINUTES` | JWT access token lifetime in minutes | `30` |
| `JWT_REFRESH_DAYS` | JWT refresh token lifetime in days | `7` |
| `GOOGLE_CLIENT_ID` | Google OAuth client ID | *(empty - Google auth disabled)* |
| `FIELD_ENCRYPTION_KEY` | Encryption key for sensitive data | `default-insecure-encryption-key-change-this` |

### Models Service Configuration

| Variable | Description | Default |
|----------|-------------|---------|
| `GROQ_API_KEY` | Groq API key for audio transcription | *(empty - feature disabled)* |
| `BACKBOARD_API_KEY` | Backboard API key for text processing | *(empty - feature disabled)* |
| `ALLOWED_ORIGINS` | CORS allowed origins | `http://localhost:3000,http://localhost:5173,http://localhost:8000` |

### Database Configuration

| Variable | Description | Default |
|----------|-------------|---------|
| `POSTGRES_DB` | PostgreSQL database name | `finsight_db` |
| `POSTGRES_USER` | PostgreSQL username | `finsight_user` |
| `POSTGRES_PASSWORD` | PostgreSQL password | `finsight_password` |
| `POSTGRES_PORT` | PostgreSQL host port | `5432` |

## Docker Compose Commands

### View Running Services

```bash
docker compose ps
```

### View Service Logs

```bash
# All services
docker compose logs -f

# Specific service
docker compose logs -f backend
docker compose logs -f models
docker compose logs -f frontend
```

### Stop Services

```bash
docker compose down
```

### Rebuild Services

After changing code or dependencies:

```bash
docker compose build
docker compose up -d
```

### Restart a Service

```bash
docker compose restart backend
```

### Execute Commands in Containers

```bash
# Django commands
docker compose exec backend python manage.py migrate
docker compose exec backend python manage.py createsuperuser
docker compose exec backend python manage.py shell

# Access container shell
docker compose exec backend bash
docker compose exec frontend sh
docker compose exec models bash
```

## Service Architecture

```
┌──────────────────┐
│   Frontend       │
│  (React/Vite)    │
│   Port: 5173     │
└────────┬─────────┘
         │
         ├─────────────────┐
         │                 │
┌────────▼─────────┐ ┌────▼───────────┐
│   Backend        │ │   Models       │
│   (Django)       │ │   (FastAPI)    │
│   Port: 8000     │ │   Port: 8001   │
└────────┬─────────┘ └────────────────┘
         │
┌────────▼─────────┐
│   PostgreSQL     │
│   Port: 5432     │
└──────────────────┘
```

## Troubleshooting

### Services Won't Start

Check service logs:
```bash
docker compose logs
```

### Database Connection Issues

Ensure PostgreSQL is healthy:
```bash
docker compose ps postgres
```

Wait for the database to be ready:
```bash
docker compose exec postgres pg_isready -U finsight_user
```

### Port Already in Use

If a port is already in use, you can change it in `docker-compose.yml` or stop the conflicting service.

### Reset Everything

To completely reset (including database):
```bash
docker compose down -v
docker compose up -d
docker compose exec backend python manage.py migrate
```

## Development vs Production

This Docker setup is configured for **development**. For production:

1. Change all default passwords and secrets in `.env`
2. Set `DJANGO_DEBUG=False`
3. Configure proper email credentials
4. Generate a secure `DJANGO_SECRET_KEY`
5. Generate a secure `FIELD_ENCRYPTION_KEY`
6. Use proper SSL/TLS certificates
7. Configure a reverse proxy (nginx, Caddy, etc.)
8. Set up proper backup strategies for PostgreSQL

## Testing the Setup

Run the test script to verify the Docker setup:

```bash
./test_docker_setup.sh
```

## Additional Resources

- [Quick Start Guide](QUICK_START.md)
- [Integration Guide](INTEGRATION_GUIDE.md)
- [API Documentation](documentation.md)
