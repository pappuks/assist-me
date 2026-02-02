"""WhatsApp tools for MCP server.

IMPORTANT: WhatsApp does not provide an official API for personal accounts.
The WhatsApp Business API exists but is for business use only.

This module provides placeholder tools and documents potential approaches:
1. WhatsApp Web scraping (requires active WhatsApp Web session)
2. Database access (requires access to WhatsApp's local database on Android/iOS)
3. Third-party libraries (e.g., whatsapp-web.js for Node.js, yowsup for Python - unofficial)

For production use, consider:
- WhatsApp Business API (for business accounts only)
- User consent and privacy considerations
- Terms of Service compliance

Reference discussions:
- https://github.com/wong2/awesome-mcp-servers (check for WhatsApp integrations)
"""

from typing import List, Dict, Any
from mcp.server.fastmcp import FastMCP


def register_whatsapp_tools(mcp: FastMCP):
    """Register WhatsApp-related tools with the MCP server.

    Note: These are placeholder tools. WhatsApp does not provide an official API
    for personal accounts. See docs/whatsapp_setup.md for implementation options.
    """

    @mcp.tool()
    async def whatsapp_check_availability() -> Dict[str, Any]:
        """Check WhatsApp integration status and available options.

        Returns:
            Status and available implementation approaches
        """
        return {
            "status": "not_implemented",
            "reason": "WhatsApp does not provide an official API for personal accounts",
            "available_approaches": [
                {
                    "method": "WhatsApp Business API",
                    "description": "Official API for business accounts only",
                    "requires": "WhatsApp Business account, Meta Business verification",
                    "limitations": "Cannot access personal WhatsApp messages",
                    "url": "https://developers.facebook.com/docs/whatsapp",
                },
                {
                    "method": "WhatsApp Web Automation",
                    "description": "Automate WhatsApp Web using browser automation",
                    "libraries": ["whatsapp-web.js (Node.js)", "selenium (Python)"],
                    "requires": "Active WhatsApp Web session, QR code authentication",
                    "limitations": "Unofficial, may violate ToS, requires active session",
                    "risks": "Account ban risk, maintenance overhead",
                },
                {
                    "method": "Local Database Access",
                    "description": "Read WhatsApp's local database (Android/iOS)",
                    "requires": "Physical device access, root/jailbreak for full access",
                    "limitations": "Read-only, requires device backup or root access",
                    "databases": [
                        "Android: /data/data/com.whatsapp/databases/msgstore.db",
                        "iOS: WhatsApp backup in iTunes/iCloud",
                    ],
                },
            ],
            "recommendation": (
                "For personal use, WhatsApp integration is technically challenging and may "
                "violate Terms of Service. Consider alternative messaging platforms with "
                "official APIs (Slack, Telegram, Discord). For business use, use WhatsApp "
                "Business API. See docs/whatsapp_setup.md for detailed implementation options."
            ),
            "documentation": "docs/whatsapp_setup.md",
        }

    @mcp.tool()
    async def whatsapp_placeholder_read_messages() -> Dict[str, str]:
        """Placeholder for reading WhatsApp messages.

        Returns:
            Instructions for implementing WhatsApp integration
        """
        return {
            "status": "not_implemented",
            "message": (
                "WhatsApp message reading is not implemented due to lack of official API. "
                "See whatsapp_check_availability tool for implementation options."
            ),
            "next_steps": "Review docs/whatsapp_setup.md for implementation guidance",
        }

    @mcp.tool()
    async def whatsapp_placeholder_search_messages(query: str) -> Dict[str, str]:
        """Placeholder for searching WhatsApp messages.

        Args:
            query: Search query

        Returns:
            Instructions for implementing WhatsApp integration
        """
        return {
            "status": "not_implemented",
            "query": query,
            "message": (
                "WhatsApp message search is not implemented due to lack of official API. "
                "See whatsapp_check_availability tool for implementation options."
            ),
            "next_steps": "Review docs/whatsapp_setup.md for implementation guidance",
        }

    @mcp.tool()
    async def whatsapp_placeholder_list_chats() -> Dict[str, str]:
        """Placeholder for listing WhatsApp chats.

        Returns:
            Instructions for implementing WhatsApp integration
        """
        return {
            "status": "not_implemented",
            "message": (
                "WhatsApp chat listing is not implemented due to lack of official API. "
                "See whatsapp_check_availability tool for implementation options."
            ),
            "alternatives": [
                "Use Telegram API (official, well-documented)",
                "Use Slack API (already implemented in this server)",
                "Use WhatsApp Business API for business accounts",
            ],
            "next_steps": "Review docs/whatsapp_setup.md for implementation guidance",
        }
