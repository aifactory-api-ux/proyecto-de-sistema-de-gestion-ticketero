"""Utility functions for the ticket system.

Provides helper functions for notifications and other
backend operations.
"""

import os
import logging
from typing import Optional

# Configure logging
logger = logging.getLogger(__name__)

# Telegram bot token from environment
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

# Enable/disable notifications
NOTIFICATIONS_ENABLED = os.getenv("NOTIFICATIONS_ENABLED", "true").lower() == "true"


def notify_telegram_user(telegram_id: int, message: str) -> bool:
    """Send a notification message to a Telegram user.
    
    Args:
        telegram_id: The Telegram user ID to send the message to.
        message: The message content to send.
    
    Returns:
        True if the notification was sent successfully, False otherwise.
    
    Raises:
        ValueError: If telegram_id is not provided or message is empty.
    """
    if not telegram_id:
        logger.warning("Cannot send notification: no telegram_id provided")
        return False
    
    if not message:
        logger.warning("Cannot send notification: empty message")
        return False
    
    if not NOTIFICATIONS_ENABLED:
        logger.info(f"Notifications disabled: skipping message to {telegram_id}")
        return True
    
    if not TELEGRAM_BOT_TOKEN:
        logger.warning("TELEGRAM_BOT_TOKEN not configured, skipping notification")
        return False
    
    try:
        import telegram
        
        bot = telegram.Bot(token=TELEGRAM_BOT_TOKEN)
        bot.send_message(chat_id=telegram_id, text=message)
        logger.info(f"Notification sent successfully to user {telegram_id}")
        return True
        
    except ImportError:
        logger.error("telegram package not installed. Install python-telegram-bot")
        return False
    except Exception as e:
        logger.error(f"Failed to send notification to {telegram_id}: {str(e)}")
        return False


def format_ticket_notification(ticket_number: int, status: str, position: Optional[int] = None) -> str:
    """Format a notification message for a ticket status update.
    
    Args:
        ticket_number: The ticket number.
        status: The current status of the ticket.
        position: Optional position in queue.
    
    Returns:
        Formatted message string.
    """
    status_messages = {
        "waiting": f"Su turno #{ticket_number} ha sido registrado. Está en espera.",
        "attended": f"Su turno #{ticket_number} está siendo atentido ahora.",
        "completed": f"Su turno #{ticket_number} ha sido completado. Gracias por su visita."
    }
    
    message = status_messages.get(status, f"Su turno #{ticket_number} tiene estado: {status}")
    
    if position is not None and status == "waiting":
        message += f"\nPosición en cola: {position}"
    
    return message


def validate_telegram_token() -> bool:
    """Validate that Telegram bot token is configured.
    
    Returns:
        True if token is configured and valid format, False otherwise.
    """
    if not TELEGRAM_BOT_TOKEN:
        logger.warning("TELEGRAM_BOT_TOKEN environment variable not set")
        return False
    
    # Basic format validation (bot tokens are typically in format: id-string)
    if len(TELEGRAM_BOT_TOKEN) < 10:
        logger.warning("TELEGRAM_BOT_TOKEN appears to be invalid format")
        return False
    
    return True


def get_queue_eta(ticket_position: int) -> str:
    """Calculate estimated wait time for a ticket position.
    
    Args:
        ticket_position: Position in the waiting queue.
    
    Returns:
        Human-readable estimated wait time.
    """
    # Estimate 3 minutes per ticket in queue
    minutes = ticket_position * 3
    
    if minutes < 1:
        return "menos de un minuto"
    elif minutes == 1:
        return "aproximadamente 1 minuto"
    elif minutes < 60:
        return f"aproximadamente {minutes} minutos"
    else:
        hours = minutes // 60
        mins = minutes % 60
        if mins == 0:
            return f"aproximadamente {hours} hora{'s' if hours > 1 else ''}"
        return f"aproximadamente {hours}h {mins}m"
