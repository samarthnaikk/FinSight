# FinSight AI

FinSight AI is an end-to-end financial intelligence platform that transforms unstructured voice calls and complex financial documents into structured, actionable insights. The system leverages advanced speech-to-text, NLP, and multimodal AI to analyze customer support calls, advisory conversations, and earnings discussions, extracting key financial entities, intents, risks, and compliance signals.

## Features
- Advanced speech-to-text and NLP for voice call analysis
- Multimodal AI for document processing (200+ formats: invoices, bank statements, contracts, loan agreements, reports)
- Accurate data extraction, validation, and normalization beyond rule-based OCR
- Integration with Backboard.io APIs for workflow automation and analytics dashboards
- Real-time financial decision support for enterprises

## Tech Stack
- Python (backend, AI/ML)
- React (frontend)
- PostgreSQL (database)
- Docker (containerization)

## Getting Started

### Prerequisites
- Python 3.8+
- Node.js 16+
- Docker and Docker Compose
- PostgreSQL (via Docker)

### Quick Start

#### 1. Set up PostgreSQL Database

```bash
# Start PostgreSQL container
docker compose up -d

# Verify the container is running
docker compose ps
```

#### 2. Configure Backend

```bash
cd backend

# Copy environment template
cp .env.example .env

# Edit .env with your configuration
# The default PostgreSQL settings work with the provided docker-compose.yml
```

#### 3. Install Backend Dependencies

```bash
cd backend
pip install -r requirements.txt
```

#### 4. Run Database Migrations

```bash
cd backend
python manage.py migrate
```

#### 5. Start the Services

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
npm install
npm run dev
```

### Database Setup

The application now uses PostgreSQL instead of SQLite. For detailed PostgreSQL setup instructions, see [POSTGRESQL_SETUP.md](POSTGRESQL_SETUP.md).

**Key Points:**
- PostgreSQL runs in a Docker container for easy setup
- Database and tables are created automatically on first run
- Environment variables configure the database connection
- All existing API endpoints work identically with PostgreSQL

## API Integration
- Backboard.io APIs for workflow automation and analytics

## Documentation
- [PostgreSQL Setup Guide](POSTGRESQL_SETUP.md) - Database configuration and troubleshooting
- [Quick Start Guide](QUICK_START.md) - Fast setup for development
- [Backend Documentation](backend/documentation.md) - API and backend details

## License
MIT License

## Contact
For inquiries, reach out to the project maintainers.
