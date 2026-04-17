#!/bin/bash
# Startup script for backend container

set -e

echo "Starting ticket management backend..."

# Validate environment
echo "Checking environment variables..."
if [ -z "$TELEGRAM_BOT_TOKEN" ]; then
    echo "WARNING: TELEGRAM_BOT_TOKEN not set - Telegram features will be disabled"
fi

# Initialize database
echo "Initializing database..."
python -c "from backend.database import init_db; init_db()"

# Start the application
echo "Starting FastAPI application..."
exec python -m uvicorn backend.main:app \
    --host "${BACKEND_HOST:-0.0.0.0}" \
    --port "${BACKEND_PORT:-8001}" \
    --reload
