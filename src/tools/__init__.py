"""MCP tools for various integrations."""

from .gmail import register_gmail_tools
from .calendar import register_calendar_tools
from .slack import register_slack_tools
from .imessage import register_imessage_tools
from .notes import register_notes_tools
from .whatsapp import register_whatsapp_tools
from .amazon import register_amazon_tools

__all__ = [
    "register_gmail_tools",
    "register_calendar_tools",
    "register_slack_tools",
    "register_imessage_tools",
    "register_notes_tools",
    "register_whatsapp_tools",
    "register_amazon_tools",
]
