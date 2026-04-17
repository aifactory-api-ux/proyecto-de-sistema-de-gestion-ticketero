"""Telegram API endpoints.

Implements webhook endpoints for Telegram bot integration:
- POST /api/telegram/status - Get ticket status via Telegram
- POST /api/telegram/notify - Send notification to user via Telegram
"""

import logging
from fastapi import APIRouter, HTTPException, status

from backend.database import get_db, get_ticket_by_id, get_ticket_position
from backend.shared.models import (
    TicketStatusRequest,
    TicketStatusResponse,
    TelegramNotification,
)
from backend.utils import notify_telegram_user

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/telegram", tags=["telegram"])


@router.post("/status", response_model=TicketStatusResponse)
def get_ticket_status_telegram(request: TicketStatusRequest) -> dict:
    """Get ticket status via Telegram bot webhook.
    
    Args:
        request: Contains ticket_id to check.
    
    Returns:
        Ticket status information.
    
    Raises:
        HTTPException: If ticket not found.
    """
    logger.info(f"Checking status for ticket_id: {request.ticket_id}")
    
    db = get_db()
    try:
        ticket = get_ticket_by_id(db, request.ticket_id)
        
        if not ticket:
            logger.warning(f"Ticket {request.ticket_id} not found")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Ticket {request.ticket_id} not found"
            )
        
        position = get_ticket_position(db, request.ticket_id)
        
        logger.info(f"Ticket {request.ticket_id} status: {ticket['status']}, position: {position}")
        
        return TicketStatusResponse(
            ticket_id=request.ticket_id,
            position=position,
            status=ticket["status"],
            number=ticket["number"]
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting ticket status: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get ticket status: {str(e)}"
        )
    finally:
        db.close()


@router.post("/notify")
def notify_user(request: TelegramNotification) -> dict:
    """Send notification to a user via Telegram.
    
    Args:
        request: Contains telegram_id and message.
    
    Returns:
        Confirmation of successful notification.
    
    Raises:
        HTTPException: If notification fails.
    """
    logger.info(f"Sending notification to telegram_id: {request.telegram_id}")
    
    if not request.telegram_id:
        logger.warning("Attempted to notify without telegram_id")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="telegram_id is required"
        )
    
    try:
        notify_telegram_user(
            telegram_id=request.telegram_id,
            message=request.message
        )
        logger.info(f"Notification sent successfully to {request.telegram_id}")
        return {"ok": True}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to send notification: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to send notification: {str(e)}"
        )
