# PostgreSQL Migration Guide

## Overview

FinSight has been migrated from SQLite to PostgreSQL for improved scalability, performance, and production readiness.

## Quick Start with Docker

### 1. Start PostgreSQL Container

```bash
# Start PostgreSQL using docker compose
docker compose up -d

# Verify the container is running
docker compose ps
```

The PostgreSQL container will:
- Create the database `finsight_db` automatically
- Create user `finsight_user` with password `finsight_password`
- Be accessible on port `5432`

### 2. Configure Backend

Create a `.env` file in the `backend/` directory:

```bash
cd backend
cp .env.example .env
# Edit .env with your actual values
```

The PostgreSQL connection is configured via environment variables in `.env`:
```
DB_ENGINE=django.db.backends.postgresql
DB_NAME=finsight_db
DB_USER=finsight_user
DB_PASSWORD=finsight_password
DB_HOST=localhost
DB_PORT=5432
```

### 3. Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### 4. Run Migrations

Django migrations will create all required tables automatically:

```bash
cd backend
python manage.py migrate
```

### 5. Create Superuser (Optional)

```bash
python manage.py createsuperuser
```

### 6. Start the Backend

```bash
python manage.py runserver 8000
```

## Database Management

### Accessing the PostgreSQL Database

```bash
# Using docker compose
docker compose exec postgres psql -U finsight_user -d finsight_db

# Or using psql directly (if installed)
psql -h localhost -U finsight_user -d finsight_db
```

### Stopping PostgreSQL

```bash
docker compose down
```

### Stopping and Removing Data

```bash
# This will delete all data in the database
docker compose down -v
```

## Configuration Options

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `DB_ENGINE` | `django.db.backends.postgresql` | Django database backend |
| `DB_NAME` | `finsight_db` | Database name |
| `DB_USER` | `finsight_user` | Database user |
| `DB_PASSWORD` | `finsight_password` | Database password |
| `DB_HOST` | `localhost` | Database host |
| `DB_PORT` | `5432` | Database port |

### Custom Configuration

To use different database credentials:

1. Update `docker-compose.yml` environment variables
2. Update `backend/.env` to match
3. Restart the PostgreSQL container

```yaml
# docker-compose.yml
environment:
  POSTGRES_DB: my_custom_db
  POSTGRES_USER: my_user
  POSTGRES_PASSWORD: my_password
```

```bash
# backend/.env
DB_NAME=my_custom_db
DB_USER=my_user
DB_PASSWORD=my_password
```

## Troubleshooting

### Connection Refused

If you get "connection refused" errors:

1. Ensure PostgreSQL container is running: `docker compose ps`
2. Check container logs: `docker compose logs postgres`
3. Verify port 5432 is not in use: `lsof -i :5432`

### Migration Errors

If migrations fail:

1. Ensure the database is accessible
2. Check database credentials in `.env`
3. Try running migrations with verbose output:
   ```bash
   python manage.py migrate --verbosity 2
   ```

### Permission Errors

If you encounter permission errors:

```bash
# Connect to the database
docker compose exec postgres psql -U finsight_user -d finsight_db

# Grant permissions
GRANT ALL PRIVILEGES ON DATABASE finsight_db TO finsight_user;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO finsight_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO finsight_user;
```

## Production Deployment

For production:

1. **Change default credentials** in both `docker-compose.yml` and `.env`
2. Use strong, randomly generated passwords
3. Consider using environment-specific configuration
4. Set `DJANGO_DEBUG=False`
5. Configure proper backup strategies
6. Use connection pooling (e.g., pgbouncer) for better performance

## Migration from SQLite

If you have existing data in SQLite:

1. Export data from SQLite:
   ```bash
   python manage.py dumpdata > data.json
   ```

2. Set up PostgreSQL and run migrations

3. Import data into PostgreSQL:
   ```bash
   python manage.py loaddata data.json
   ```

## Healthcheck

The PostgreSQL container includes a healthcheck that ensures the database is ready to accept connections:

```bash
# Check container health
docker compose ps
```

The container will show as "healthy" when PostgreSQL is fully initialized and ready.
