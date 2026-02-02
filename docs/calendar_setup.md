# Google Calendar Setup Guide

This guide explains how to set up Google Calendar integration for the Assist-Me MCP server.

## Prerequisites

- Google account with Google Calendar
- Access to Google Cloud Console
- Same project as Gmail setup (recommended)

## Step 1: Create/Use Google Cloud Project

If you already set up Gmail, use the same project. Otherwise:

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one

## Step 2: Enable Google Calendar API

1. In Google Cloud Console, go to **APIs & Services > Library**
2. Search for "Google Calendar API"
3. Click on "Google Calendar API" and click **Enable**

## Step 3: Create OAuth 2.0 Credentials

If you already have OAuth credentials from Gmail setup, you can reuse them. The Calendar tools will use the same client ID and secret but request different scopes.

If creating new credentials:

1. Go to **APIs & Services > Credentials**
2. Click **Create Credentials** > **OAuth client ID**
3. Configure OAuth consent screen if not done already
4. Add scope: `https://www.googleapis.com/auth/calendar`
5. Create OAuth client ID (Desktop app)

## Step 4: Configure Environment Variables

Use the same `.env` file as Gmail (they share credentials):

```bash
GOOGLE_CLIENT_ID=your-client-id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=your-client-secret
GOOGLE_REDIRECT_URI=http://localhost:8080/oauth2callback
```

## Step 5: Authenticate

1. Run the MCP server
2. When you use a Calendar tool, authentication will occur automatically
3. Grant calendar permissions when prompted
4. Credentials saved in `.credentials/default_calendar_token.json`

## Available Tools

### List Tools
- `calendar_list_calendars` - List all calendars
- `calendar_list_events` - List events in a date range
- `calendar_list_accounts` - List authenticated accounts

### Create/Modify Tools
- `calendar_create_event` - Create a new event
- `calendar_update_event` - Update an existing event
- `calendar_delete_event` - Delete an event

## Usage Examples

### List Calendars
```python
await calendar_list_calendars(account_id="default")
```

### List Upcoming Events
```python
# Next 7 days (default)
await calendar_list_events(calendar_id="primary")

# Custom date range
await calendar_list_events(
    calendar_id="primary",
    time_min="2024-03-01T00:00:00Z",
    time_max="2024-03-31T23:59:59Z",
    max_results=50
)
```

### Create an Event
```python
await calendar_create_event(
    summary="Team Meeting",
    start_time="2024-03-15T10:00:00-07:00",
    end_time="2024-03-15T11:00:00-07:00",
    description="Quarterly planning meeting",
    location="Conference Room A",
    attendees=["colleague@example.com"],
    calendar_id="primary"
)
```

### Update an Event
```python
await calendar_update_event(
    event_id="event123",
    summary="Team Meeting (Updated)",
    start_time="2024-03-15T14:00:00-07:00",
    end_time="2024-03-15T15:00:00-07:00",
    calendar_id="primary"
)
```

### Delete an Event
```python
await calendar_delete_event(
    event_id="event123",
    calendar_id="primary"
)
```

## Multiple Calendars

To work with different calendars:

1. First, list all calendars to get their IDs
2. Use the calendar ID in subsequent calls

```python
# List all calendars
calendars = await calendar_list_calendars()
# Returns: [{"id": "primary", ...}, {"id": "work@example.com", ...}]

# Use specific calendar
await calendar_list_events(calendar_id="work@example.com")
```

## Date/Time Format

All date/time values should be in ISO 8601 format:

- **With timezone**: `2024-03-15T10:00:00-07:00`
- **UTC**: `2024-03-15T17:00:00Z`

The server uses UTC by default but you can specify timezone in your requests.

## Troubleshooting

### Authentication Issues

- **"Calendar API not enabled"**: Enable Google Calendar API in Cloud Console
- **Token expired**: Delete `.credentials/default_calendar_token.json` and re-authenticate
- **Permission denied**: Ensure the OAuth consent screen includes Calendar scope

### Event Creation Issues

- **Invalid time format**: Use ISO 8601 format (e.g., `2024-03-15T10:00:00-07:00`)
- **Past event creation**: Some calendars may restrict creating events in the past
- **Attendee notifications**: Calendar may require additional permissions to send invites

### Multiple Account Issues

Similar to Gmail, use different `account_id` values:

```python
await calendar_list_events(account_id="work", calendar_id="primary")
await calendar_list_events(account_id="personal", calendar_id="primary")
```

## Security Notes

- Calendar write access is powerful - be cautious with event creation/deletion
- Review permissions regularly in [Google Account Permissions](https://myaccount.google.com/permissions)
- Keep credentials secure and never commit to version control
- Consider using read-only scopes if you don't need write access

## References

- Inspired by:
  - [mcp-google-workspace](https://github.com/j3k0/mcp-google-workspace)
  - [google-calendar-mcp](https://github.com/nspady/google-calendar-mcp)
  - [mcp-google-calendar](https://github.com/guinacio/mcp-google-calendar)
- [Google Calendar API Documentation](https://developers.google.com/calendar/api)
- [ISO 8601 Date/Time Format](https://en.wikipedia.org/wiki/ISO_8601)
