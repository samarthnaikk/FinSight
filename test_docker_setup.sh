#!/bin/bash
# Script to test Docker setup for FinSight application

set -e

echo "======================================"
echo "Testing FinSight Docker Setup"
echo "======================================"
echo ""

# Check if Docker is available
if ! command -v docker &> /dev/null; then
    echo "❌ Error: Docker is not installed"
    exit 1
fi
echo "✓ Docker is available"

# Check if Docker Compose is available
if ! docker compose version &> /dev/null; then
    echo "❌ Error: Docker Compose is not installed"
    exit 1
fi
echo "✓ Docker Compose is available"

# Validate docker-compose.yml
echo ""
echo "Validating docker-compose.yml..."
if docker compose config > /dev/null 2>&1; then
    echo "✓ docker-compose.yml is valid"
else
    echo "❌ Error: docker-compose.yml has syntax errors"
    exit 1
fi

# Check if Dockerfiles exist
echo ""
echo "Checking Dockerfiles..."
for dir in backend frontend models; do
    if [ -f "$dir/Dockerfile" ]; then
        echo "✓ $dir/Dockerfile exists"
    else
        echo "❌ Error: $dir/Dockerfile not found"
        exit 1
    fi
done

# Check if .env.example exists
echo ""
if [ -f ".env.example" ]; then
    echo "✓ .env.example exists"
else
    echo "❌ Error: .env.example not found"
    exit 1
fi

echo ""
echo "======================================"
echo "Build and Start Services"
echo "======================================"
echo ""
echo "Building services (this may take a few minutes)..."
docker compose build

echo ""
echo "Starting services..."
docker compose up -d

echo ""
echo "Waiting for services to start..."
sleep 10

echo ""
echo "======================================"
echo "Service Status"
echo "======================================"
docker compose ps

echo ""
echo "======================================"
echo "Testing Service Endpoints"
echo "======================================"

# Test backend health
echo ""
echo "Testing backend (http://localhost:8000)..."
if curl -s -f http://localhost:8000/api/auth/me/ > /dev/null 2>&1; then
    echo "✓ Backend is responding"
else
    echo "⚠ Backend is not responding (may need authentication)"
fi

# Test models health
echo ""
echo "Testing models service (http://localhost:8001)..."
if curl -s -f http://localhost:8001/health > /dev/null 2>&1; then
    echo "✓ Models service is responding"
else
    echo "❌ Models service is not responding"
fi

# Test frontend
echo ""
echo "Testing frontend (http://localhost:5173)..."
if curl -s -f http://localhost:5173 > /dev/null 2>&1; then
    echo "✓ Frontend is responding"
else
    echo "❌ Frontend is not responding"
fi

echo ""
echo "======================================"
echo "Testing with Missing Environment Variables"
echo "======================================"
echo ""
echo "Checking logs for environment variable errors..."
if docker compose logs | grep -i "error.*environment\|missing.*variable" > /dev/null 2>&1; then
    echo "❌ Services have environment variable errors"
    docker compose logs | grep -i "error.*environment\|missing.*variable" | head -10
else
    echo "✓ No environment variable errors detected"
fi

echo ""
echo "======================================"
echo "✅ Docker Setup Test Complete"
echo "======================================"
echo ""
echo "To stop services: docker compose down"
echo "To view logs: docker compose logs -f"
echo "To restart: docker compose restart"
