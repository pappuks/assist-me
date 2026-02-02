"""Slack tools for MCP server.

Uses the Slack SDK to interact with Slack workspaces.
Reference: https://slack.dev/python-slack-sdk/
"""

from typing import Optional, List, Dict, Any
from mcp.server.fastmcp import FastMCP
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError


def register_slack_tools(mcp: FastMCP, slack_token: Optional[str] = None):
    """Register Slack-related tools with the MCP server.

    Args:
        mcp: FastMCP server instance
        slack_token: Slack bot or user token
    """

    if not slack_token:
        # Register a placeholder tool that explains authentication is needed
        @mcp.tool()
        async def slack_authentication_required() -> str:
            """Slack tools require authentication.

            Returns:
                Instructions for setting up Slack authentication
            """
            return (
                "Slack authentication required. Please set SLACK_BOT_TOKEN or "
                "SLACK_USER_TOKEN in your .env file. See docs/slack_setup.md for details."
            )

        return

    client = WebClient(token=slack_token)

    @mcp.tool()
    async def slack_list_channels(
        types: str = "public_channel,private_channel",
        limit: int = 100,
    ) -> List[Dict[str, Any]]:
        """List Slack channels.

        Args:
            types: Comma-separated channel types (default: "public_channel,private_channel")
            limit: Maximum number of channels to return (default: 100)

        Returns:
            List of channels with id, name, and details
        """
        try:
            response = client.conversations_list(types=types, limit=limit)
            channels = response["channels"]
            return [
                {
                    "id": ch["id"],
                    "name": ch["name"],
                    "is_private": ch.get("is_private", False),
                    "is_member": ch.get("is_member", False),
                    "topic": ch.get("topic", {}).get("value", ""),
                    "purpose": ch.get("purpose", {}).get("value", ""),
                }
                for ch in channels
            ]
        except SlackApiError as e:
            raise RuntimeError(f"Failed to list Slack channels: {e.response['error']}")

    @mcp.tool()
    async def slack_read_messages(
        channel_id: str,
        limit: int = 20,
        oldest: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """Read messages from a Slack channel.

        Args:
            channel_id: Channel ID to read from
            limit: Maximum number of messages to return (default: 20)
            oldest: Only messages after this Unix timestamp (optional)

        Returns:
            List of messages with text, user, and timestamp
        """
        try:
            kwargs = {"channel": channel_id, "limit": limit}
            if oldest:
                kwargs["oldest"] = oldest

            response = client.conversations_history(**kwargs)
            messages = response["messages"]

            formatted_messages = []
            for msg in messages:
                formatted_messages.append(
                    {
                        "type": msg.get("type"),
                        "user": msg.get("user"),
                        "text": msg.get("text", ""),
                        "timestamp": msg.get("ts"),
                        "thread_ts": msg.get("thread_ts"),
                    }
                )

            return formatted_messages
        except SlackApiError as e:
            raise RuntimeError(f"Failed to read Slack messages: {e.response['error']}")

    @mcp.tool()
    async def slack_search_messages(
        query: str,
        count: int = 20,
    ) -> List[Dict[str, Any]]:
        """Search for messages across all channels.

        Args:
            query: Search query
            count: Maximum number of results (default: 20)

        Returns:
            List of matching messages
        """
        try:
            response = client.search_messages(query=query, count=count)
            matches = response["messages"]["matches"]

            return [
                {
                    "text": msg.get("text", ""),
                    "username": msg.get("username"),
                    "channel": msg.get("channel", {}).get("name"),
                    "timestamp": msg.get("ts"),
                    "permalink": msg.get("permalink"),
                }
                for msg in matches
            ]
        except SlackApiError as e:
            raise RuntimeError(f"Failed to search Slack messages: {e.response['error']}")

    @mcp.tool()
    async def slack_get_thread(
        channel_id: str,
        thread_ts: str,
    ) -> List[Dict[str, Any]]:
        """Get all messages in a thread.

        Args:
            channel_id: Channel ID
            thread_ts: Thread timestamp

        Returns:
            List of messages in the thread
        """
        try:
            response = client.conversations_replies(channel=channel_id, ts=thread_ts)
            messages = response["messages"]

            return [
                {
                    "user": msg.get("user"),
                    "text": msg.get("text", ""),
                    "timestamp": msg.get("ts"),
                }
                for msg in messages
            ]
        except SlackApiError as e:
            raise RuntimeError(f"Failed to get Slack thread: {e.response['error']}")

    @mcp.tool()
    async def slack_list_users(limit: int = 100) -> List[Dict[str, str]]:
        """List users in the Slack workspace.

        Args:
            limit: Maximum number of users to return (default: 100)

        Returns:
            List of users with id, name, and real name
        """
        try:
            response = client.users_list(limit=limit)
            users = response["members"]

            return [
                {
                    "id": user["id"],
                    "name": user.get("name", ""),
                    "real_name": user.get("real_name", ""),
                    "email": user.get("profile", {}).get("email", ""),
                    "is_bot": user.get("is_bot", False),
                }
                for user in users
                if not user.get("deleted", False)
            ]
        except SlackApiError as e:
            raise RuntimeError(f"Failed to list Slack users: {e.response['error']}")
