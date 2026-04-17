"""API package for ticket management endpoints.


Implements REST endpoints for ticket management and Telegram integration.
"""

from fastapi import APIRouter

# Import routers from submodules
from backend.api.tickets import router as tickets_router
from backend.api.telegram import router as telegram_router

# Export routers for main.py to register
__all__ = [
    "tickets_router",
    "telegram_router",
]
