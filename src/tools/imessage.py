"""iMessage tools for MCP server (macOS only).

Uses direct SQLite database access to read Messages data on macOS.
This approach is more reliable than AppleScript and provides better functionality.

Note: Requires macOS and Full Disk Access permission for the application.
"""

import sqlite3
import platform
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Any, Optional
from mcp.server.fastmcp import FastMCP


def _is_macos() -> bool:
    """Check if running on macOS."""
    return platform.system() == "Darwin"


def _get_messages_db_path() -> Path:
    """Get the path to the Messages database."""
    return Path.home() / "Library" / "Messages" / "chat.db"


def _check_db_access() -> tuple[bool, Optional[str]]:
    """Check if the Messages database is accessible.

    Returns:
        Tuple of (is_accessible, error_message)
    """
    if not _is_macos():
        return False, "iMessage tools are only available on macOS"

    db_path = _get_messages_db_path()

    if not db_path.exists():
        return False, f"Messages database not found at {db_path}"

    try:
        # Try to open the database in read-only mode
        conn = sqlite3.connect(f"file:{db_path}?mode=ro", uri=True)
        conn.close()
        return True, None
    except sqlite3.OperationalError as e:
        if "unable to open database file" in str(e).lower():
            return False, (
                "Unable to access Messages database. Full Disk Access permission required.\n"
                "Grant access in: System Settings > Privacy & Security > Full Disk Access\n"
                "Add your terminal app or Python to the list and restart the application."
            )
        return False, f"Database access error: {str(e)}"
    except Exception as e:
        return False, f"Unexpected error accessing database: {str(e)}"


def _convert_apple_timestamp(timestamp: int) -> str:
    """Convert Apple's timestamp (seconds since 2001-01-01) to readable format.

    Args:
        timestamp: Apple timestamp in nanoseconds

    Returns:
        ISO format datetime string
    """
    if timestamp == 0:
        return "Unknown"

    # Convert nanoseconds to seconds and adjust for Apple epoch (2001-01-01)
    apple_epoch = datetime(2001, 1, 1)
    actual_seconds = timestamp / 1_000_000_000  # Convert nanoseconds to seconds

    try:
        dt = apple_epoch + timedelta(seconds=actual_seconds)
        return dt.isoformat()
    except (ValueError, OverflowError):
        return "Invalid date"


def _execute_query(query: str, params: tuple = ()) -> List[tuple]:
    """Execute a query on the Messages database.

    Args:
        query: SQL query to execute
        params: Query parameters

    Returns:
        List of result tuples

    Raises:
        RuntimeError: If database access fails
    """
    accessible, error = _check_db_access()
    if not accessible:
        raise RuntimeError(error)

    db_path = _get_messages_db_path()

    try:
        conn = sqlite3.connect(f"file:{db_path}?mode=ro", uri=True)
        cursor = conn.cursor()
        cursor.execute(query, params)
        results = cursor.fetchall()
        conn.close()
        return results
    except Exception as e:
        raise RuntimeError(f"Database query failed: {str(e)}")


def register_imessage_tools(mcp: FastMCP):
    """Register iMessage-related tools with the MCP server.

    Note: These tools only work on macOS and require Full Disk Access permission.
    """

    @mcp.tool()
    async def imessage_check_availability() -> Dict[str, Any]:
        """Check if iMessage tools are available on this system.

        Returns:
            Availability status, platform info, and setup instructions
        """
        accessible, error = _check_db_access()

        return {
            "available": accessible,
            "platform": platform.system(),
            "database_path": str(_get_messages_db_path()),
            "error": error if not accessible else None,
            "requirements": [
                "macOS operating system",
                "Messages app with message history",
                "Full Disk Access permission for this application",
            ],
            "setup_instructions": (
                "1. Open System Settings (or System Preferences)\n"
                "2. Go to Privacy & Security > Full Disk Access\n"
                "3. Click the lock to make changes\n"
                "4. Click '+' and add your Terminal app or Python\n"
                "5. Restart the application after granting access"
            ) if not accessible else None,
        }

    @mcp.tool()
    async def imessage_list_recent_conversations(limit: int = 20) -> List[Dict[str, Any]]:
        """List recent iMessage conversations with last message info.

        Args:
            limit: Maximum number of conversations to return (default: 20, max: 100)

        Returns:
            List of recent conversations with contact, last message, and timestamp
        """
        limit = min(limit, 100)  # Cap at 100 for performance

        try:
            query = """
            SELECT
                h.id as contact,
                MAX(m.date) as last_date,
                (SELECT text FROM message
                 WHERE handle_id = h.ROWID
                 ORDER BY date DESC LIMIT 1) as last_message,
                COUNT(m.ROWID) as message_count
            FROM message m
            JOIN handle h ON m.handle_id = h.ROWID
            WHERE m.text IS NOT NULL
            GROUP BY h.id
            ORDER BY last_date DESC
            LIMIT ?
            """

            results = _execute_query(query, (limit,))

            conversations = []
            for contact, last_date, last_message, msg_count in results:
                conversations.append({
                    "contact": contact,
                    "last_message": last_message[:100] + "..." if last_message and len(last_message) > 100 else last_message,
                    "last_message_date": _convert_apple_timestamp(last_date),
                    "total_messages": msg_count,
                })

            return conversations

        except RuntimeError as e:
            return [{"error": str(e)}]
        except Exception as e:
            return [{"error": f"Failed to list conversations: {str(e)}"}]

    @mcp.tool()
    async def imessage_read_messages(
        contact: str,
        limit: int = 50,
    ) -> List[Dict[str, Any]]:
        """Read recent messages from a specific contact or phone number.

        Args:
            contact: Contact phone number (e.g., +15551234567) or email
            limit: Maximum number of messages to return (default: 50, max: 200)

        Returns:
            List of messages with text, timestamp, and sender info
        """
        limit = min(limit, 200)  # Cap at 200 for performance

        try:
            query = """
            SELECT
                m.text,
                m.date,
                m.is_from_me,
                h.id as contact_id,
                m.cache_has_attachments
            FROM message m
            JOIN handle h ON m.handle_id = h.ROWID
            WHERE h.id = ?
            AND m.text IS NOT NULL
            ORDER BY m.date DESC
            LIMIT ?
            """

            results = _execute_query(query, (contact, limit))

            if not results:
                # Try to find similar contacts
                search_query = """
                SELECT DISTINCT h.id
                FROM handle h
                WHERE h.id LIKE ?
                LIMIT 5
                """
                similar = _execute_query(search_query, (f"%{contact}%",))

                if similar:
                    return [{
                        "error": f"No messages found for '{contact}'",
                        "suggestion": "Try one of these contacts:",
                        "similar_contacts": [s[0] for s in similar]
                    }]
                else:
                    return [{
                        "error": f"No messages found for '{contact}'",
                        "note": "Make sure to use the full phone number (e.g., +15551234567) or email address"
                    }]

            messages = []
            for text, date, is_from_me, contact_id, has_attachments in results:
                messages.append({
                    "text": text,
                    "date": _convert_apple_timestamp(date),
                    "from": "me" if is_from_me else contact_id,
                    "is_from_me": bool(is_from_me),
                    "has_attachments": bool(has_attachments),
                })

            # Return in chronological order (oldest first)
            messages.reverse()

            return messages

        except RuntimeError as e:
            return [{"error": str(e)}]
        except Exception as e:
            return [{"error": f"Failed to read messages: {str(e)}"}]

    @mcp.tool()
    async def imessage_search_messages(
        query: str,
        limit: int = 50,
        contact: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Search for messages containing specific text.

        Args:
            query: Search text to find in messages
            limit: Maximum number of results (default: 50, max: 200)
            contact: Optional contact to limit search to specific conversation

        Returns:
            List of matching messages with context
        """
        limit = min(limit, 200)  # Cap at 200 for performance

        try:
            if contact:
                sql_query = """
                SELECT
                    m.text,
                    m.date,
                    m.is_from_me,
                    h.id as contact_id
                FROM message m
                JOIN handle h ON m.handle_id = h.ROWID
                WHERE h.id = ?
                AND m.text LIKE ?
                ORDER BY m.date DESC
                LIMIT ?
                """
                params = (contact, f"%{query}%", limit)
            else:
                sql_query = """
                SELECT
                    m.text,
                    m.date,
                    m.is_from_me,
                    h.id as contact_id
                FROM message m
                JOIN handle h ON m.handle_id = h.ROWID
                WHERE m.text LIKE ?
                ORDER BY m.date DESC
                LIMIT ?
                """
                params = (f"%{query}%", limit)

            results = _execute_query(sql_query, params)

            if not results:
                return [{
                    "message": f"No messages found containing '{query}'",
                    "searched_contact": contact if contact else "all contacts"
                }]

            messages = []
            for text, date, is_from_me, contact_id in results:
                messages.append({
                    "text": text,
                    "date": _convert_apple_timestamp(date),
                    "contact": contact_id,
                    "from": "me" if is_from_me else contact_id,
                    "is_from_me": bool(is_from_me),
                })

            return messages

        except RuntimeError as e:
            return [{"error": str(e)}]
        except Exception as e:
            return [{"error": f"Failed to search messages: {str(e)}"}]

    @mcp.tool()
    async def imessage_get_contact_list() -> List[Dict[str, Any]]:
        """Get a list of all contacts you've messaged with.

        Returns:
            List of contacts with their identifiers (phone numbers or emails)
        """
        try:
            query = """
            SELECT DISTINCT
                h.id as contact,
                COUNT(m.ROWID) as message_count,
                MAX(m.date) as last_contact
            FROM handle h
            JOIN message m ON m.handle_id = h.ROWID
            GROUP BY h.id
            HAVING message_count > 0
            ORDER BY last_contact DESC
            """

            results = _execute_query(query)

            contacts = []
            for contact, msg_count, last_date in results:
                contacts.append({
                    "contact": contact,
                    "message_count": msg_count,
                    "last_contact": _convert_apple_timestamp(last_date),
                })

            return contacts

        except RuntimeError as e:
            return [{"error": str(e)}]
        except Exception as e:
            return [{"error": f"Failed to get contact list: {str(e)}"}]
