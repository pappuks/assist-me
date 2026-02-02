"""Gmail tools for MCP server.

Inspired by:
- https://github.com/j3k0/mcp-google-workspace
- https://github.com/taylorwilsdon/google_workspace_mcp
"""

import base64
from typing import Optional, List, Dict, Any
from email.mime.text import MIMEText
from mcp.server.fastmcp import FastMCP
from ..services.oauth import GoogleOAuthManager


def register_gmail_tools(mcp: FastMCP, oauth_manager: GoogleOAuthManager):
    """Register Gmail-related tools with the MCP server."""

    @mcp.tool()
    async def gmail_list_messages(
        account_id: str = "default",
        query: str = "",
        max_results: int = 10,
    ) -> List[Dict[str, Any]]:
        """List Gmail messages with optional query.

        Args:
            account_id: Google account identifier (default: "default")
            query: Gmail search query (e.g., "is:unread", "from:example@gmail.com")
            max_results: Maximum number of messages to return (default: 10)

        Returns:
            List of message summaries with id, threadId, and snippet
        """
        try:
            service = oauth_manager.build_gmail_service(account_id)
            results = (
                service.users()
                .messages()
                .list(userId="me", q=query, maxResults=max_results)
                .execute()
            )
            messages = results.get("messages", [])

            # Fetch full message details
            detailed_messages = []
            for msg in messages:
                msg_detail = (
                    service.users().messages().get(userId="me", id=msg["id"]).execute()
                )

                # Extract headers
                headers = msg_detail.get("payload", {}).get("headers", [])
                subject = next(
                    (h["value"] for h in headers if h["name"].lower() == "subject"), ""
                )
                from_email = next(
                    (h["value"] for h in headers if h["name"].lower() == "from"), ""
                )
                date = next(
                    (h["value"] for h in headers if h["name"].lower() == "date"), ""
                )

                detailed_messages.append(
                    {
                        "id": msg_detail["id"],
                        "threadId": msg_detail["threadId"],
                        "subject": subject,
                        "from": from_email,
                        "date": date,
                        "snippet": msg_detail.get("snippet", ""),
                    }
                )

            return detailed_messages
        except Exception as e:
            raise RuntimeError(f"Failed to list Gmail messages: {str(e)}")

    @mcp.tool()
    async def gmail_get_message(
        message_id: str,
        account_id: str = "default",
    ) -> Dict[str, Any]:
        """Get full details of a specific Gmail message.

        Args:
            message_id: Gmail message ID
            account_id: Google account identifier (default: "default")

        Returns:
            Full message details including body, headers, and attachments
        """
        try:
            service = oauth_manager.build_gmail_service(account_id)
            message = (
                service.users().messages().get(userId="me", id=message_id, format="full").execute()
            )

            # Extract headers
            headers = message.get("payload", {}).get("headers", [])
            subject = next((h["value"] for h in headers if h["name"].lower() == "subject"), "")
            from_email = next((h["value"] for h in headers if h["name"].lower() == "from"), "")
            to_email = next((h["value"] for h in headers if h["name"].lower() == "to"), "")
            date = next((h["value"] for h in headers if h["name"].lower() == "date"), "")

            # Extract body
            body = ""
            if "parts" in message["payload"]:
                for part in message["payload"]["parts"]:
                    if part["mimeType"] == "text/plain":
                        body_data = part["body"].get("data", "")
                        body = base64.urlsafe_b64decode(body_data).decode("utf-8")
                        break
            else:
                body_data = message["payload"]["body"].get("data", "")
                if body_data:
                    body = base64.urlsafe_b64decode(body_data).decode("utf-8")

            return {
                "id": message["id"],
                "threadId": message["threadId"],
                "subject": subject,
                "from": from_email,
                "to": to_email,
                "date": date,
                "body": body,
                "snippet": message.get("snippet", ""),
                "labelIds": message.get("labelIds", []),
            }
        except Exception as e:
            raise RuntimeError(f"Failed to get Gmail message: {str(e)}")

    @mcp.tool()
    async def gmail_search(
        query: str,
        account_id: str = "default",
        max_results: int = 20,
    ) -> List[Dict[str, Any]]:
        """Search Gmail messages using advanced Gmail search syntax.

        Args:
            query: Gmail search query (e.g., "from:john@example.com subject:meeting")
            account_id: Google account identifier (default: "default")
            max_results: Maximum number of results (default: 20)

        Returns:
            List of matching messages

        Examples:
            - "is:unread" - Unread messages
            - "from:example@gmail.com" - Messages from specific sender
            - "subject:invoice after:2024/01/01" - Messages with subject containing "invoice" after date
            - "has:attachment larger:5M" - Messages with attachments larger than 5MB
        """
        return await gmail_list_messages(account_id, query, max_results)

    @mcp.tool()
    async def gmail_list_labels(account_id: str = "default") -> List[Dict[str, str]]:
        """List all Gmail labels.

        Args:
            account_id: Google account identifier (default: "default")

        Returns:
            List of labels with id and name
        """
        try:
            service = oauth_manager.build_gmail_service(account_id)
            results = service.users().labels().list(userId="me").execute()
            labels = results.get("labels", [])
            return [{"id": label["id"], "name": label["name"]} for label in labels]
        except Exception as e:
            raise RuntimeError(f"Failed to list Gmail labels: {str(e)}")

    @mcp.tool()
    async def gmail_list_accounts() -> List[str]:
        """List all authenticated Gmail accounts.

        Returns:
            List of account IDs that have been authenticated
        """
        try:
            accounts = oauth_manager.list_authenticated_accounts("gmail")
            return accounts if accounts else ["No accounts authenticated yet"]
        except Exception as e:
            raise RuntimeError(f"Failed to list Gmail accounts: {str(e)}")
