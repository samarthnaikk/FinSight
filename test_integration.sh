#!/bin/bash

# Test script for FinSight API Integration
# This script tests the connectivity to Backend and Models services

echo "==================================="
echo "FinSight Integration Test Script"
echo "==================================="
echo ""

# Test Backend
echo "Testing Backend Service (Port 8000)..."
BACKEND_HEALTH=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/api/auth/me/ 2>/dev/null || echo "000")

if [ "$BACKEND_HEALTH" = "401" ] || [ "$BACKEND_HEALTH" = "403" ]; then
    echo "✓ Backend is running on port 8000 (returns $BACKEND_HEALTH as expected for unauthenticated request)"
elif [ "$BACKEND_HEALTH" = "000" ]; then
    echo "✗ Backend is NOT running on port 8000"
    echo "  Start it with: cd backend && python manage.py runserver 8000"
else
    echo "? Backend returned unexpected status: $BACKEND_HEALTH"
fi
echo ""

# Test Models Service
echo "Testing Models Service (Port 8001)..."
MODELS_HEALTH=$(curl -s http://localhost:8001/health 2>/dev/null)

if [ -n "$MODELS_HEALTH" ]; then
    echo "✓ Models service is running on port 8001"
    echo "  Response: $MODELS_HEALTH"
else
    echo "✗ Models service is NOT running on port 8001"
    echo "  Start it with: cd models && python -m uvicorn app:app --host 0.0.0.0 --port 8001"
fi
echo ""

# Test Models Root Endpoint
echo "Testing Models Root Endpoint..."
MODELS_ROOT=$(curl -s http://localhost:8001/ 2>/dev/null | grep -o "FinSight")

if [ -n "$MODELS_ROOT" ]; then
    echo "✓ Models root endpoint is accessible"
else
    echo "✗ Models root endpoint is not accessible"
fi
echo ""

# Summary
echo "==================================="
echo "Test Summary"
echo "==================================="
echo "Backend (Port 8000): Check logs above"
echo "Models (Port 8001): Check logs above"
echo ""
echo "If services are not running, start them:"
echo "  1. Backend:  cd backend && python manage.py runserver 8000"
echo "  2. Models:   cd models && python -m uvicorn app:app --host 0.0.0.0 --port 8001"
echo "  3. Frontend: cd frontend && npm run dev"
echo ""
echo "Then access the application at: http://localhost:5173"
