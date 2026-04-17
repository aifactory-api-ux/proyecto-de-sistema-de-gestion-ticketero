#!/bin/bash
# Startup script for frontend container

set -e

echo "Starting frontend static server..."

# Default port for static server
FRONTEND_PORT="${FRONTEND_PORT:-8080}"

# Serve static files using Python's http.server
exec python3 -m http.server "$FRONTEND_PORT" --directory /app
