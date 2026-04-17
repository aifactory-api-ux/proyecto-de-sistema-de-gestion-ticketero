"""Pydantic models for the ticket system.

Defines all data contracts used throughout the backend.
These models ensure type safety and validation for API requests and responses.
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class TicketCreate(BaseModel):
    """Model for creating a new ticket.

    
    Attributes:
        user_name: Name of the user requesting the ticket.
        telegram_id: Optional Telegram user ID for notifications.
    """
    user_name: str = Field(..., max_length=100, description="Name of the user requesting the ticket")
    telegram_id: Optional[int] = Field(None, description="Telegram user ID for notifications")


class Ticket(BaseModel):
    """Complete ticket model with all fields.
    
    Attributes:
        id: Unique ticket identifier.
        user_name: Name of the user who requested the ticket.
        telegram_id: Optional Telegram user ID.
        number: Assigned ticket number in the queue.
        status: Current status of the ticket (waiting, attended, completed).
        created_at: Timestamp when the ticket was created.
        updated_at: Timestamp of the last status update.
    """
    id: int = Field(..., description="Unique ticket identifier")
    user_name: str = Field(..., max_length=100, description="Name of the user")
    telegram_id: Optional[int] = Field(None, description="Telegram user ID")
    number: int = Field(..., description="Assigned ticket number in the queue")
    status: str = Field(..., description="Current status of the ticket")
    created_at: datetime = Field(..., description="Ticket creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")


class TicketStatusRequest(BaseModel):
    """Request model for checking ticket status.
    
    Attributes:
        ticket_id: ID of the ticket to check.
    """
    ticket_id: int = Field(..., description="ID of the ticket to check")


class TicketStatusResponse(BaseModel):
    """Response model for ticket status queries.
    
    Attributes:
        ticket_id: ID of the queried ticket.
        position: Current position in the queue.
        status: Current status of the ticket.
        number: Ticket number.
    """
    ticket_id: int = Field(..., description="ID of the ticket")
    position: int = Field(..., description="Current position in the queue")
    status: str = Field(..., description="Current status of the ticket")
    number: int = Field(..., description="Ticket number")


class TelegramNotification(BaseModel):
    """Model for sending Telegram notifications.
    
    Attributes:
        telegram_id: Target Telegram user ID.
        message: Message content to send.
    """
    telegram_id: int = Field(..., description="Target Telegram user ID")
    message: str = Field(..., description="Message content to send")
