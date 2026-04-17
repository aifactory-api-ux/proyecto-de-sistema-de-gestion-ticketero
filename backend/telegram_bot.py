"""Telegram Bot integration for ticket notifications and status queries.

This module provides the Telegram bot functionality for:
- Notifying users when their ticket status changes
- Responding to status queries from users
- Handling /start and /status commands
"""

import logging
import os
from typing import Optional

from telegram import Update, Bot
from telegram.ext import Application, CommandHandler, MessageHandler, filters, Contexts

# Configure logging
logger = logging.getLogger(__name__)

# Get bot token from environment
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

# Global bot instance
_bot: Optional[Bot] = None
_application: Optional[Application] = None


async def start_command(update: Update, context: Contexts.DEFAULT_TYPE) -> None:
    """Handle the /start command.
    
    Args:
        update: Telegram update object.
        context: Bot context object.
    """
    await update.message.reply_text(
        "¡Bienvenido al sistema de turnos!\n\n"
        "Comandos disponibles:\n"
        "• /start - Ver este mensaje\n"
        "• /status <ticket_id> - Consultar estado de un turno\n"
        "• /help - Ver ayuda"
    )


async def help_command(update: Update, context: Contexts.DEFAULT_TYPE) -> None:
    """Handle the /help command.
    
    Args:
        update: Telegram update object.
        context: Bot context object.
    """
    await update.message.reply_text(
        "📋 Sistema de Turnos - Ayuda\n\n"
        "Crea un turno desde la web: http://localhost:8080\n\n"
        "Comandos:\n"
        "• /start - Iniciar\n"
        "• /status <id> - Consultar estado de tu turno\n"
        "• /help - Ver esta ayuda\n\n"
        "Cuando tu turno sea llamado, recibirás una notificación."
    )


async def status_command(update: Update, context: Contexts.DEFAULT_TYPE) -> None:
    """Handle the /status command to check ticket status.
    
    Args:
        update: Telegram update object.
        context: Bot context object containing parsed args.
    """
    # Get ticket_id from command arguments
    if not context.args:
        await update.message.reply_text(
            "Por favor proporciona el ID del turno.\n"
            "Ejemplo: /status 1"
        )
        return

    try:
        ticket_id = int(context.args[0])
    except ValueError:
        await update.message.reply_text(
            "ID de turno inválido. Por favor ingresa un número.\n"
            "Ejemplo: /status 1"
        )
        return

    # Import here to avoid circular imports
    from backend.database import get_db, get_ticket_by_id, get_ticket_position
    from backend.utils import notify_telegram_user

    with get_db() as conn:
        ticket = get_ticket_by_id(conn, ticket_id)

        if not ticket:
            await update.message.reply_text(
                f"No se encontró el turno con ID {ticket_id}."
            )
            return

        position = get_ticket_position(conn, ticket_id)
        status_text = {
            "waiting": "En espera",
            "attended": "En atención",
            "completed": "Completado"
        }.get(ticket["status"], ticket["status"])

        message = (
            f"🎫 Turno #{ticket['number']}\n"
            f"Estado: {status_text}\n"
        )

        if ticket["status"] == "waiting":
            message += f"Posición: {position}° en la cola"
        elif ticket["status"] == "attended":
            message += "Tu turno está siendo atendido ahora"
        else:
            message += "Tu turno ha sido completado"

        await update.message.reply_text(message)


async def echo_handler(update: Update, context: Contexts.DEFAULT_TYPE) -> None:
    """Handle unknown messages.
    
    Args:
        update: Telegram update object.
        context: Bot context object.
    """
    await update.message.reply_text(
        "Comando no reconocido. Usa /help para ver los comandos disponibles."
    )


async def post_init(application: Application) -> None:
    """Post-initialization hook for the application.
    
    Args:
        application: The bot application instance.
    """
    global _bot
    _bot = application.bot
    logger.info("Telegram bot initialized successfully")
    
    # Set webhook if URL is provided
    webhook_url = os.getenv("TELEGRAM_WEBHOOK_URL")
    if webhook_url:
        await application.bot.set_webhook(url=f"{webhook_url}/webhook")
        logger.info(f"Webhook set to {webhook_url}/webhook")


def start_bot() -> Application:
    """Start the Telegram bot.
    
    Returns:
        The running application instance.
    
    Raises:
        ValueError: If TELEGRAM_BOT_TOKEN is not set.
    """
    global _application
    
    if not TELEGRAM_BOT_TOKEN:
        raise ValueError("TELEGRAM_BOT_TOKEN environment variable is required")
    
    # Create the application
    _application = (
        Application.builder()
        .token(TELEGRAM_BOT_TOKEN)
        .post_init(post_init)
        .build()
    )
    
    # Add command handlers
    _application.add_handler(CommandHandler("start", start_command))
    _application.add_handler(CommandHandler("help", help_command))
    _application.add_handler(CommandHandler("status", status_command))
    
    # Add echo handler for unknown messages
    _application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo_handler))
    
    logger.info("Starting Telegram bot polling...")
    
    # Run the bot
    _application.run_polling(allowed_updates=Update.ALL_TYPES)
    
    return _application


async def handle_new_ticket(telegram_id: int, ticket_number: int, user_name: str) -> bool:
    """Send notification to user when a new ticket is created.
    
    Args:
        telegram_id: The user's Telegram ID.
        ticket_number: The assigned ticket number.
        user_name: The name of the user.
    
    Returns:
        True if notification was sent successfully, False otherwise.
    """
    global _bot
    
    if not _bot:
        logger.warning("Bot not initialized, cannot send notification")
        return False
    
    try:
        message = (
            f"✅ Turno creado exitosamente!\n\n"
            f"👤 Nombre: {user_name}\n"
            f"🎫 Número de turno: {ticket_number}\n\n"
            f"Por favor espera tu turno. Te notificaremos cuando sea tu momento."
        )
        
        await _bot.send_message(chat_id=telegram_id, text=message)
        logger.info(f"Notification sent to {telegram_id} for ticket {ticket_number}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to send notification to {telegram_id}: {e}")
        return False


async def handle_status_request(telegram_id: int, ticket_id: int) -> dict:
    """Handle a status query from a Telegram user.
    
    Args:
        telegram_id: The user's Telegram ID.
        ticket_id: The ticket ID to query.
    
    Returns:
        Dictionary with status information or error message.
    """
    global _bot
    
    if not _bot:
        logger.warning("Bot not initialized, cannot respond")
        return {"error": "Bot not initialized"}
    
    from backend.database import get_db, get_ticket_by_id, get_ticket_position
    
    with get_db() as conn:
        ticket = get_ticket_by_id(conn, ticket_id)
        
        if not ticket:
            return {
                "ticket_id": ticket_id,
                "status": "not_found",
                "message": "Ticket no encontrado"
            }
        
        position = get_ticket_position(conn, ticket_id)
        status_text = {
            "waiting": "En espera",
            "attended": "En atención",
            "completed": "Completado"
        }.get(ticket["status"], ticket["status"])
        
        return {
            "ticket_id": ticket_id,
            "position": position,
            "status": ticket["status"],
            "number": ticket["number"],
            "status_text": status_text
        }


async def notify_user(telegram_id: int, message: str) -> bool:
    """Send a notification message to a specific user.
    
    Args:
        telegram_id: The user's Telegram ID.
        message: The message to send.
    
    Returns:
        True if notification was sent successfully, False otherwise.
    """
    global _bot
    
    if not _bot:
        logger.warning("Bot not initialized, cannot send notification")
        return False
    
    try:
        await _bot.send_message(chat_id=telegram_id, text=message)
        logger.info(f"Notification sent to {telegram_id}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to send notification to {telegram_id}: {e}")
        return False


def get_bot() -> Optional[Bot]:
    """Get the current bot instance.
    
    Returns:
        The Bot instance or None if not initialized.
    """
    return _bot


def is_bot_initialized() -> bool:
    """Check if the bot is initialized.
    
    Returns:
        True if bot is initialized, False otherwise.
    """
    return _bot is not None
