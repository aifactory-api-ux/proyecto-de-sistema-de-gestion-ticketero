"""Ticket API endpoints.

Implements REST endpoints for ticket management:
- POST /api/tickets - Create new ticket
- GET /api/tickets - Get all tickets
- GET /api/tickets/{ticket_id}/status - Get ticket status
- PATCH /api/tickets/{ticket_id} - Update ticket status
"""

from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

from backend.database import (
    get_db,
    create_ticket,
    get_ticket_by_id,
    get_all_tickets,
    update_ticket_status,
    get_ticket_position,
)
from backend.shared.models import (
    TicketCreate,
    Ticket,
    TicketStatusResponse,
)
from backend.utils import notify_telegram_user

router = APIRouter(prefix="/api/tickets", tags=["tickets"])


class StatusUpdate(BaseModel):
    """Request model for updating ticket status."""
    status: str


def _get_status_notification_message(ticket_number: int, status: str) -> str:
    status_messages = {
        "waiting": f"Tu turno #{ticket_number} está en espera.",
        "attended": f"👋 Tu turno #{ticket_number} está siendo atendido",
        "completed": f"✔ Turno #{ticket_number} completado. Gracias por usar nuestro servicio.",
        "cancelled": f"❌ Turno #{ticket_number} ha sido cancelado"
    }
    return status_messages.get(status, f"Actualización de turno #{ticket_number}: {status}")


@router.post("", response_model=Ticket, status_code=status.HTTP_201_CREATED)
def create_ticket_endpoint(
    ticket_data: TicketCreate,
    db=None
) -> dict:
    """Create a new ticket.
    
    Args:
        ticket_data: Ticket creation data with user_name and optional telegram_id.
    
    
    Returns:
        The created ticket with assigned ID, number, and timestamps.
    
    Raises:
        HTTPException: If ticket creation fails.
    """
    try:
        db = get_db()
        ticket = create_ticket(
            db=db,
            user_name=ticket_data.user_name,
            telegram_id=ticket_data.telegram_id
        )
        
        # Send notification if telegram_id provided
        if ticket_data.telegram_id:
            try:
                notify_telegram_user(
                    telegram_id=ticket_data.telegram_id,
                    message=f"Tu turno ha sido creado: #{ticket['number']}"
                )
            except Exception as e:
                # Log but don't fail the request
                import logging
                logging.getLogger(__name__).warning(f"Failed to send notification: {e}")
        
        return ticket
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to create ticket: {str(e)}"
        )


@router.get("", response_model=List[Ticket])
def get_all_tickets_endpoint(db=None) -> list:
    """Get all tickets.
    
    Returns:
        List of all tickets in the system.
    """
    db = get_db()
    tickets = get_all_tickets(db)
    return tickets


@router.get("/{ticket_id}/status", response_model=TicketStatusResponse)
def get_ticket_status_endpoint(ticket_id: int, db=None) -> dict:
    """Get the status of a specific ticket.
    
    Args:
        ticket_id: ID of the ticket to check.
    
    Returns:
        Ticket status information including position in queue.
    
    Raises:
        HTTPException: If ticket not found.
    """
    db = get_db()
    ticket = get_ticket_by_id(db, ticket_id)
    
    if not ticket:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Ticket {ticket_id} not found"
        )
    
    position = get_ticket_position(db, ticket_id)
    
    return TicketStatusResponse(
        ticket_id=ticket_id,
        position=position,
        status=ticket["status"],
        number=ticket["number"]
    )


@router.patch("/{ticket_id}", response_model=Ticket)
def update_ticket_status_endpoint(
    ticket_id: int,
    status_update: StatusUpdate,
    db=None
) -> dict:
    """Update the status of a specific ticket.
    
    Args:
        ticket_id: ID of the ticket to update.
        status_update: New status value.
    
    Returns:
        The updated ticket.
    
    Raises:
        HTTPException: If ticket not found or update fails.
    """
    # Validate status
    valid_statuses = ["waiting", "attended", "completed"]
    if status_update.status not in valid_statuses:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid status. Must be one of: {', '.join(valid_statuses)}"
        )
    
    db = get_db()
    
    # Get current ticket to check if it exists and get telegram_id
    current_ticket = get_ticket_by_id(db, ticket_id)
    
    if not current_ticket:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Ticket {ticket_id} not found"
        )
    
    old_status = current_ticket["status"]
    
    try:
        ticket = update_ticket_status(db, ticket_id, status_update.status)
        
        # Send notification if status changed and telegram_id exists
        if current_ticket.get("telegram_id") and old_status != status_update.status:
            try:
                message = _get_status_notification_message(
                    ticket["number"],
                    status_update.status
                )
                notify_telegram_user(
                    telegram_id=current_ticket["telegram_id"],
                    message=message
                )
            except Exception as e:
                import logging
                logging.getLogger(__name__).warning(f"Failed to send notification: {e}")
        return ticket
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to update ticket: {str(e)}"
        )
