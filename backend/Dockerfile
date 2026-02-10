# Use Python 3.11 slim image as base
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Install system dependencies
RUN apt-get update && apt-get install -y \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements file
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . .

# Expose port
EXPOSE 8000

# Note: Database migrations must be run manually after container startup:
# docker compose exec backend python manage.py migrate
# For automated migrations, consider using an entrypoint script

# Run Django development server
# WARNING: This is for DEVELOPMENT only. For production, use Gunicorn or uWSGI
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
