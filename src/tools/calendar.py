"""Google Calendar tools for MCP server.

Inspired by:
- https://github.com/j3k0/mcp-google-workspace
- https://github.com/nspady/google-calendar-mcp
- https://github.com/guinacio/mcp-google-calendar
"""

from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
from mcp.server.fastmcp import FastMCP
from ..services.oauth import GoogleOAuthManager


def register_calendar_tools(mcp: FastMCP, oauth_manager: GoogleOAuthManager):
    """Register Google Calendar-related tools with the MCP server."""

    @mcp.tool()
    async def calendar_list_calendars(account_id: str = "default") -> List[Dict[str, str]]:
        """List all calendars for the authenticated account.

        Args:
            account_id: Google account identifier (default: "default")

        Returns:
            List of calendars with id, name, and description
        """
        try:
            service = oauth_manager.build_calendar_service(account_id)
            calendar_list = service.calendarList().list().execute()
            calendars = calendar_list.get("items", [])
            return [
                {
                    "id": cal["id"],
                    "summary": cal.get("summary", ""),
                    "description": cal.get("description", ""),
                    "primary": cal.get("primary", False),
                }
                for cal in calendars
            ]
        except Exception as e:
            raise RuntimeError(f"Failed to list calendars: {str(e)}")

    @mcp.tool()
    async def calendar_list_events(
        calendar_id: str = "primary",
        account_id: str = "default",
        time_min: Optional[str] = None,
        time_max: Optional[str] = None,
        max_results: int = 10,
    ) -> List[Dict[str, Any]]:
        """List calendar events within a time range.

        Args:
            calendar_id: Calendar ID (default: "primary")
            account_id: Google account identifier (default: "default")
            time_min: Start time in ISO format (default: now)
            time_max: End time in ISO format (default: 7 days from now)
            max_results: Maximum number of events to return (default: 10)

        Returns:
            List of events with details
        """
        try:
            service = oauth_manager.build_calendar_service(account_id)

            # Default time range: next 7 days
            if time_min is None:
                time_min = datetime.utcnow().isoformat() + "Z"
            if time_max is None:
                time_max = (datetime.utcnow() + timedelta(days=7)).isoformat() + "Z"

            events_result = (
                service.events()
                .list(
                    calendarId=calendar_id,
                    timeMin=time_min,
                    timeMax=time_max,
                    maxResults=max_results,
                    singleEvents=True,
                    orderBy="startTime",
                )
                .execute()
            )
            events = events_result.get("items", [])

            formatted_events = []
            for event in events:
                start = event["start"].get("dateTime", event["start"].get("date"))
                end = event["end"].get("dateTime", event["end"].get("date"))
                formatted_events.append(
                    {
                        "id": event["id"],
                        "summary": event.get("summary", "No title"),
                        "description": event.get("description", ""),
                        "start": start,
                        "end": end,
                        "location": event.get("location", ""),
                        "attendees": [
                            a.get("email") for a in event.get("attendees", [])
                        ],
                    }
                )

            return formatted_events
        except Exception as e:
            raise RuntimeError(f"Failed to list calendar events: {str(e)}")

    @mcp.tool()
    async def calendar_create_event(
        summary: str,
        start_time: str,
        end_time: str,
        calendar_id: str = "primary",
        account_id: str = "default",
        description: Optional[str] = None,
        location: Optional[str] = None,
        attendees: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """Create a new calendar event.

        Args:
            summary: Event title
            start_time: Start time in ISO format (e.g., "2024-03-15T10:00:00-07:00")
            end_time: End time in ISO format
            calendar_id: Calendar ID (default: "primary")
            account_id: Google account identifier (default: "default")
            description: Event description (optional)
            location: Event location (optional)
            attendees: List of attendee email addresses (optional)

        Returns:
            Created event details including event ID and link
        """
        try:
            service = oauth_manager.build_calendar_service(account_id)

            event = {
                "summary": summary,
                "start": {"dateTime": start_time, "timeZone": "UTC"},
                "end": {"dateTime": end_time, "timeZone": "UTC"},
            }

            if description:
                event["description"] = description
            if location:
                event["location"] = location
            if attendees:
                event["attendees"] = [{"email": email} for email in attendees]

            created_event = (
                service.events().insert(calendarId=calendar_id, body=event).execute()
            )

            return {
                "id": created_event["id"],
                "summary": created_event.get("summary"),
                "start": created_event["start"].get("dateTime"),
                "end": created_event["end"].get("dateTime"),
                "htmlLink": created_event.get("htmlLink"),
                "status": "created",
            }
        except Exception as e:
            raise RuntimeError(f"Failed to create calendar event: {str(e)}")

    @mcp.tool()
    async def calendar_delete_event(
        event_id: str,
        calendar_id: str = "primary",
        account_id: str = "default",
    ) -> Dict[str, str]:
        """Delete a calendar event.

        Args:
            event_id: Event ID to delete
            calendar_id: Calendar ID (default: "primary")
            account_id: Google account identifier (default: "default")

        Returns:
            Status message
        """
        try:
            service = oauth_manager.build_calendar_service(account_id)
            service.events().delete(calendarId=calendar_id, eventId=event_id).execute()
            return {"status": "deleted", "event_id": event_id}
        except Exception as e:
            raise RuntimeError(f"Failed to delete calendar event: {str(e)}")

    @mcp.tool()
    async def calendar_update_event(
        event_id: str,
        calendar_id: str = "primary",
        account_id: str = "default",
        summary: Optional[str] = None,
        start_time: Optional[str] = None,
        end_time: Optional[str] = None,
        description: Optional[str] = None,
        location: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Update an existing calendar event.

        Args:
            event_id: Event ID to update
            calendar_id: Calendar ID (default: "primary")
            account_id: Google account identifier (default: "default")
            summary: New event title (optional)
            start_time: New start time in ISO format (optional)
            end_time: New end time in ISO format (optional)
            description: New description (optional)
            location: New location (optional)

        Returns:
            Updated event details
        """
        try:
            service = oauth_manager.build_calendar_service(account_id)

            # Get existing event
            event = service.events().get(calendarId=calendar_id, eventId=event_id).execute()

            # Update fields
            if summary:
                event["summary"] = summary
            if start_time:
                event["start"] = {"dateTime": start_time, "timeZone": "UTC"}
            if end_time:
                event["end"] = {"dateTime": end_time, "timeZone": "UTC"}
            if description:
                event["description"] = description
            if location:
                event["location"] = location

            updated_event = (
                service.events()
                .update(calendarId=calendar_id, eventId=event_id, body=event)
                .execute()
            )

            return {
                "id": updated_event["id"],
                "summary": updated_event.get("summary"),
                "start": updated_event["start"].get("dateTime"),
                "end": updated_event["end"].get("dateTime"),
                "htmlLink": updated_event.get("htmlLink"),
                "status": "updated",
            }
        except Exception as e:
            raise RuntimeError(f"Failed to update calendar event: {str(e)}")

    @mcp.tool()
    async def calendar_list_accounts() -> List[str]:
        """List all authenticated Calendar accounts.

        Returns:
            List of account IDs that have been authenticated
        """
        try:
            accounts = oauth_manager.list_authenticated_accounts("calendar")
            return accounts if accounts else ["No accounts authenticated yet"]
        except Exception as e:
            raise RuntimeError(f"Failed to list Calendar accounts: {str(e)}")
