"""Main FastAPI application entry point.

Implements the backend REST API for the ticket management system.
Includes:
- Health check endpoint
- Ticket management endpoints
- Telegram bot integration
"""

import os
import sys
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# Configure logging
logging.basicConfig(
    level=logging.DEBUG if os.getenv("DEBUG") else logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


# Validate required environment variables
REQUIRED_ENV_VARS = {
    "TELEGRAM_BOT_TOKEN": os.getenv("TELEGRAM_BOT_TOKEN"),
}


def validate_environment():
    """Validate that all required environment variables are set."""
    missing = [k for k, v in REQUIRED_ENV_VARS.items() if not v]
    if missing:
        # TELEGRAM_BOT_TOKEN is optional for MVP
        logger.warning(f"Optional env vars not set: {missing}")
    logger.info("Environment validation complete")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler for startup and shutdown."""
    # Startup
    logger.info("Starting application...")
    validate_environment()
    
    # Initialize database
    try:
        from backend.database import init_db
        init_db()
        logger.info("Database initialized")
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        raise
    
    # Start Telegram bot in background (optional)
    try:
        import threading
        from backend.telegram_bot import start_bot
        
        bot_thread = threading.Thread(target=start_bot, daemon=True)
        bot_thread.start()
        logger.info("Telegram bot thread started")
    except Exception as e:
        logger.warning(f"Telegram bot not started: {e}")
    
    yield
    
    # Shutdown
    logger.info("Shutting down application...")


# Create FastAPI app
app = FastAPI(
    title="Ticket Management API",
    description="REST API for ticket management system with Telegram integration",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Health check endpoint
@app.get("/health", tags=["health"])
def health_check() -> dict:
    """Health check endpoint.
    
    Returns:
        Health status of the service.
    """
    return {
        "status": "healthy",
        "service": "ticket-api",
        "version": "1.0.0"
    }


# Load routers
try:
    from backend.api.tickets import router as tickets_router
    app.include_router(tickets_router)
    logger.info("Tickets router loaded")
except ImportError as e:
    logger.error(f"Failed to load tickets router: {e}")

try:
    from backend.api.telegram import router as telegram_router
    app.include_router(telegram_router)
    logger.info("Telegram router loaded")
except ImportError as e:
    logger.error(f"Failed to load telegram router: {e}")


# Root endpoint
@app.get("/", tags=["root"])
def root() -> dict:
    """Root endpoint with API information."""
    return {
        "name": "Ticket Management API",
        "version": "1.0.0",
        "docs": "/docs"
    }


if __name__ == "__main__":
    import uvicorn
    
    host = os.getenv("BACKEND_HOST", "0.0.0.0")
    port = int(os.getenv("BACKEND_PORT", "8001"))
    
    logger.info(f"Starting server on {host}:{port}")
    uvicorn.run(
        "backend.main:app",
        host=host,
        port=port,
        reload=os.getenv("DEBUG") == "true"
    )
