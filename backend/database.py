"""Database module for SQLite ticket management.

Provides functions for creating, reading, updating tickets
and managing the SQLite database connection.
"""

import os
import sys
from datetime import datetime
from typing import Optional, List, Dict, Any
from contextlib import contextmanager

try:
    import sqlite3
except ImportError:
    # If running in an environment where sqlite3 is not available, raise a clear error
    raise ImportError("sqlite3 module is required but not found. Please ensure Python is built with SQLite support.")

# Database path from environment or default
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./tickets.db")
DB_PATH = DATABASE_URL.replace("sqlite:///", "")


def get_db_connection() -> sqlite3.Connection:
    """Get a SQLite database connection.
    
    Returns:
        SQLite connection object.
    """
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


@contextmanager
def get_db():
    """Context manager for database connection.
    
    Yields:
        SQLite connection object.
    """
    conn = get_db_connection()
    try:
        yield conn
    finally:
        conn.close()


def init_db():
    """Initialize the database schema.
    
    Creates the tickets table if it doesn't exist.
    """
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS tickets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_name TEXT NOT NULL,
                telegram_id INTEGER,
                number INTEGER NOT NULL UNIQUE,
                status TEXT NOT NULL DEFAULT 'waiting',
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_tickets_status 
            ON tickets(status)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_tickets_number 
            ON tickets(number)
        """)
        conn.commit()


def create_ticket(
    db: sqlite3.Connection,
    user_name: str,
    telegram_id: Optional[int] = None
) -> Dict[str, Any]:
    """Create a new ticket.
    
    Args:
        db: Database connection.
        user_name: Name of the user requesting the ticket.
        telegram_id: Optional Telegram user ID.
    
    Returns:
        Dictionary containing the created ticket data.
    
    Raises:
        sqlite3.Error: If database operation fails.
    """
    cursor = db.cursor()
    
    # Get the next ticket number
    cursor.execute("SELECT COALESCE(MAX(number), 0) + 1 AS next_number FROM tickets")
    next_number = cursor.fetchone()["next_number"]
    
    # Get current timestamp
    now = datetime.now().isoformat()
    
    # Insert the new ticket
    cursor.execute(
        """
        INSERT INTO tickets (user_name, telegram_id, number, status, created_at, updated_at)
        VALUES (?, ?, ?, 'waiting', ?, ?)
        """,
        (user_name, telegram_id, next_number, now, now)
    )
    
    db.commit()
    
    # Get the created ticket
    ticket_id = cursor.lastrowid
    return get_ticket_by_id(db, ticket_id)



def get_ticket_by_id(db: sqlite3.Connection, ticket_id: int) -> Optional[Dict[str, Any]]:
    """Get a ticket by its ID.
    
    Args:
        db: Database connection.
        ticket_id: ID of the ticket to retrieve.
    
    Returns:
        Dictionary containing ticket data or None if not found.
    """
    cursor = db.cursor()
    cursor.execute("SELECT * FROM tickets WHERE id = ?", (ticket_id,))
    row = cursor.fetchone()
    
    if row is None:
        return None
    
    return dict(row)



def get_all_tickets(db: sqlite3.Connection) -> List[Dict[str, Any]]:
    """Get all tickets ordered by number.
    
    Args:
        db: Database connection.
    
    Returns:
        List of dictionaries containing ticket data.
    """
    cursor = db.cursor()
    cursor.execute("SELECT * FROM tickets ORDER BY number ASC")
    rows = cursor.fetchall()
    
    return [dict(row) for row in rows]



def update_ticket_status(
    db: sqlite3.Connection,
    ticket_id: int,
    status: str
) -> Optional[Dict[str, Any]]:
    """Update the status of a ticket.
    
    Args:
        db: Database connection.
        ticket_id: ID of the ticket to update.
        status: New status ('waiting', 'attended', 'completed').
    
    Returns:
        Dictionary containing the updated ticket data or None if not found.
    
    Raises:
        ValueError: If status is invalid.
    """
    valid_statuses = ['waiting', 'attended', 'completed']
    if status not in valid_statuses:
        raise ValueError(f"Invalid status. Must be one of: {', '.join(valid_statuses)}")
    
    cursor = db.cursor()
    now = datetime.now().isoformat()
    
    cursor.execute(
        "UPDATE tickets SET status = ?, updated_at = ? WHERE id = ?",
        (status, now, ticket_id)
    )
    
    db.commit()
    
    # Check if ticket was found and updated
    if cursor.rowcount == 0:
        return None
    
    return get_ticket_by_id(db, ticket_id)



def get_ticket_position(db: sqlite3.Connection, ticket_id: int) -> int:
    """Get the position of a ticket in the waiting queue.
    
    Args:
        db: Database connection.
        ticket_id: ID of the ticket.
    
    Returns:
        Position in the queue (1-based), or 0 if not in waiting status.
    """
    cursor = db.cursor()
    
    # First get the ticket's number
    cursor.execute("SELECT number, status FROM tickets WHERE id = ?", (ticket_id,))
    row = cursor.fetchone()
    
    if row is None:
        return 0
    
    if row["status"] != "waiting":
        return 0
    
    # Count how many tickets are waiting with a lower number
    cursor.execute(
        """
        SELECT COUNT(*) as position 
        FROM tickets 
        WHERE status = 'waiting' AND number < (
            SELECT number FROM tickets WHERE id = ?
        )
        """,
        (ticket_id,)
    )
    
    result = cursor.fetchone()
    return result["position"] + 1


def get_next_waiting_ticket(db: sqlite3.Connection) -> Optional[Dict[str, Any]]:
    """Get the next ticket in waiting status with the lowest number.
    
    Args:
        db: Database connection.
    
    Returns:
        Dictionary containing the next ticket data or None if no waiting tickets.
    """
    cursor = db.cursor()
    cursor.execute(
        """
        SELECT * FROM tickets 
        WHERE status = 'waiting' 
        ORDER BY number ASC 
        LIMIT 1
        """
    )
    row = cursor.fetchone()
    
    if row is None:
        return None
    
    return dict(row)



def get_waiting_count(db: sqlite3.Connection) -> int:
    """Get the count of tickets in waiting status.
    
    Args:
        db: Database connection.
    
    Returns:
        Number of tickets waiting.
    """
    cursor = db.cursor()
    cursor.execute("SELECT COUNT(*) as count FROM tickets WHERE status = 'waiting'")
    return cursor.fetchone()["count"]


def delete_ticket(db: sqlite3.Connection, ticket_id: int) -> bool:
    """Delete a ticket by its ID.
    
    Args:
        db: Database connection.
        ticket_id: ID of the ticket to delete.
    
    Returns:
        True if ticket was deleted, False if not found.
    """
    cursor = db.cursor()
    cursor.execute("DELETE FROM tickets WHERE id = ?", (ticket_id,))
    db.commit()
    
    return cursor.rowcount > 0
