"""iMessage tools for MCP server (macOS only).

Uses AppleScript to access iMessage data on macOS.
Note: This requires macOS and proper permissions to access Messages.
"""

import subprocess
import platform
from typing import List, Dict, Any
from mcp.server.fastmcp import FastMCP


def _is_macos() -> bool:
    """Check if running on macOS."""
    return platform.system() == "Darwin"


def _run_applescript(script: str) -> str:
    """Execute AppleScript and return output.

    Args:
        script: AppleScript code to execute

    Returns:
        Script output as string

    Raises:
        RuntimeError: If not on macOS or script fails
    """
    if not _is_macos():
        raise RuntimeError("iMessage tools are only available on macOS")

    try:
        result = subprocess.run(
            ["osascript", "-e", script],
            capture_output=True,
            text=True,
            check=True,
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"AppleScript execution failed: {e.stderr}")


def register_imessage_tools(mcp: FastMCP):
    """Register iMessage-related tools with the MCP server.

    Note: These tools only work on macOS and require appropriate permissions.
    """

    @mcp.tool()
    async def imessage_list_recent_conversations(limit: int = 20) -> List[Dict[str, str]]:
        """List recent iMessage conversations.

        Args:
            limit: Maximum number of conversations to return (default: 20)

        Returns:
            List of recent conversations with contact info

        Note:
            Requires macOS and permission to access Messages app.
            You may need to grant Terminal/Python access in System Preferences > Privacy.
        """
        if not _is_macos():
            return [{"error": "iMessage tools are only available on macOS"}]

        try:
            script = f"""
            tell application "Messages"
                set conversationList to {{}}
                repeat with i from 1 to {limit}
                    try
                        set theChat to chat i
                        set chatName to name of theChat
                        set end of conversationList to chatName
                    end try
                end repeat
                return conversationList
            end tell
            """
            result = _run_applescript(script)
            conversations = result.split(", ") if result else []
            return [{"contact": conv} for conv in conversations]
        except Exception as e:
            return [{"error": f"Failed to list conversations: {str(e)}"}]

    @mcp.tool()
    async def imessage_read_messages(
        contact: str,
        limit: int = 20,
    ) -> List[Dict[str, Any]]:
        """Read recent messages from a specific contact or chat.

        Args:
            contact: Contact name or phone number
            limit: Maximum number of messages to return (default: 20)

        Returns:
            List of messages with text, sender, and direction

        Note:
            Requires macOS and permission to access Messages app.
        """
        if not _is_macos():
            return [{"error": "iMessage tools are only available on macOS"}]

        try:
            # Note: This is a simplified implementation. A more robust version
            # would access the Messages database directly with proper permissions.
            script = f"""
            tell application "Messages"
                set messageList to {{}}
                set targetBuddy to buddy "{contact}"
                set messageCount to count of messages in targetBuddy
                set startIndex to messageCount - {limit} + 1
                if startIndex < 1 then set startIndex to 1

                repeat with i from startIndex to messageCount
                    set theMessage to message i of targetBuddy
                    set messageText to text of theMessage
                    set messageDate to date received of theMessage
                    set end of messageList to {{messageText, messageDate as string}}
                end repeat

                return messageList
            end tell
            """
            result = _run_applescript(script)

            # Parse the result (simplified)
            return [
                {
                    "contact": contact,
                    "messages": result,
                    "note": "This is a simplified implementation. For production use, "
                    "consider accessing the Messages database directly.",
                }
            ]
        except Exception as e:
            return [
                {
                    "error": f"Failed to read messages: {str(e)}",
                    "suggestion": "You may need to grant Terminal access in System Preferences > "
                    "Security & Privacy > Privacy > Automation",
                }
            ]

    @mcp.tool()
    async def imessage_search_messages(query: str, limit: int = 20) -> List[Dict[str, str]]:
        """Search for messages containing specific text.

        Args:
            query: Search query
            limit: Maximum number of results (default: 20)

        Returns:
            List of matching messages

        Note:
            This is a basic implementation. For better search functionality,
            consider accessing the Messages database at ~/Library/Messages/chat.db
            using SQLite with proper permissions.
        """
        if not _is_macos():
            return [{"error": "iMessage tools are only available on macOS"}]

        return [
            {
                "status": "not_implemented",
                "message": "Full-text search requires direct database access.",
                "suggestion": "For advanced search, you can query the Messages database at "
                "~/Library/Messages/chat.db using SQLite. See docs/imessage_setup.md "
                "for implementation details.",
            }
        ]

    @mcp.tool()
    async def imessage_check_availability() -> Dict[str, Any]:
        """Check if iMessage tools are available on this system.

        Returns:
            Availability status and requirements
        """
        is_available = _is_macos()
        return {
            "available": is_available,
            "platform": platform.system(),
            "requirements": [
                "macOS operating system",
                "Messages app installed",
                "Terminal/Python granted access to Messages in System Preferences",
            ],
            "alternative_approach": "For production use, consider accessing the Messages "
            "database directly at ~/Library/Messages/chat.db with proper permissions.",
        }
