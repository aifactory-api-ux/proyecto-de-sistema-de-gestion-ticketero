#!/bin/bash

# Ticket System startup script
# Zero-intervention startup - auto-creates .env from .env.example if missing

set -e

echo "🎫 Ticket System - Starting..."

# Auto-create .env from .env.example on first run
if [ ! -f .env ]; then
    cp .env.example .env
    echo "✓ .env created from .env.example"
fi

# Check Docker is available
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed"
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed"
    exit 1
fi

# Check Docker daemon is running
if ! docker info &> /dev/null; then
    echo "❌ Docker daemon is not running"
    exit 1
fi

echo "✓ Docker environment validated"

# Build services
echo "📦 Building services..."
docker-compose build

# Start services
echo "🚀 Starting services..."
docker-compose up -d

# Wait for services to be healthy
echo "⏳ Waiting for services to be ready..."
timeout=60
elapsed=0
while [ $elapsed -lt $timeout ]; do
    if docker-compose ps | grep -q "Up"; then
        # Check backend health
        if curl -s http://localhost:8001/health > /dev/null 2>&1; then
            echo "✓ Backend is ready"
            break
        fi
    fi
    sleep 2
    elapsed=$((elapsed + 2))
done

# Check if services started successfully
if ! docker-compose ps | grep -q "Up"; then
    echo "❌ Failed to start services"
    docker-compose logs
    exit 1
fi

echo ""
echo "═══════════════════════════════════════"
echo "🎫 Ticket System Started Successfully!"
echo "═══════════════════════════════════════"
echo ""
echo "📍 Frontend:     http://localhost:8080"
echo "📍 API Docs:      http://localhost:8001/docs"
echo "📍 Health Check: http://localhost:8001/health"
echo ""
echo "📝 Use './run.sh' to start services"
echo "📝 Use 'docker-compose down' to stop services"
echo ""
