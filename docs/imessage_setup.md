# iMessage Setup Guide (macOS Only)

This guide explains how to set up iMessage integration for the Assist-Me MCP server.

⚠️ **Important**: iMessage tools only work on macOS systems.

## Prerequisites

- macOS operating system
- Messages app installed and configured
- Terminal/Python access to Messages (see permissions below)

## Approach

The iMessage tools use AppleScript to interact with the Messages app on macOS. This provides read-only access to your messages.

## Step 1: Grant Terminal Access

macOS requires permission for Terminal (or your Python environment) to control the Messages app:

1. Open **System Preferences/Settings**
2. Go to **Security & Privacy** > **Privacy**
3. Select **Automation** in the left sidebar
4. Find **Terminal** (or your terminal app) in the list
5. Check the box next to **Messages** to grant access

### For Python/Virtual Environments

If running from a virtual environment or Python directly:

1. You may need to grant access to `Python` or `Python.app`
2. The first time you run an iMessage tool, macOS may prompt you
3. Click **OK** to allow access

## Step 2: No Additional Configuration Required

Unlike cloud services, iMessage access doesn't require API keys or OAuth. The tools work directly with your local Messages app.

## Available Tools

- `imessage_list_recent_conversations` - List recent conversations
- `imessage_read_messages` - Read messages from a specific contact
- `imessage_search_messages` - Search messages (placeholder)
- `imessage_check_availability` - Check if iMessage tools are available

## Usage Examples

### Check Availability
```python
await imessage_check_availability()
# Returns system info and requirements
```

### List Recent Conversations
```python
await imessage_list_recent_conversations(limit=20)
# Returns list of recent contacts/chats
```

### Read Messages from a Contact
```python
await imessage_read_messages(
    contact="John Smith",  # Or phone number
    limit=20
)
```

## Current Limitations

The current implementation uses AppleScript, which has some limitations:

1. **Basic Implementation**: The AppleScript approach provides basic functionality
2. **No Full-Text Search**: Advanced search requires database access
3. **Parsing Complexity**: AppleScript output requires parsing
4. **Performance**: Slower than direct database access

## Advanced Implementation: Direct Database Access

For production use, consider accessing the Messages database directly:

### Database Location
```
~/Library/Messages/chat.db
```

### Approach

1. **Use SQLite**: The Messages database is SQLite
2. **Grant Full Disk Access**: Required to read the database
3. **Read-Only Mode**: Open database in read-only mode
4. **Query Messages**: Use SQL to query messages

### Example SQL Queries

```sql
-- List recent conversations
SELECT DISTINCT handle.id, MAX(message.date) as last_message
FROM message
JOIN handle ON message.handle_id = handle.ROWID
GROUP BY handle.id
ORDER BY last_message DESC
LIMIT 20;

-- Get messages from a specific contact
SELECT text, date, is_from_me
FROM message
JOIN handle ON message.handle_id = handle.ROWID
WHERE handle.id = '+15551234567'
ORDER BY date DESC
LIMIT 50;

-- Search messages
SELECT text, date, handle.id
FROM message
JOIN handle ON message.handle_id = handle.ROWID
WHERE text LIKE '%search term%'
ORDER BY date DESC
LIMIT 100;
```

### Implementation Example

```python
import sqlite3
from pathlib import Path

db_path = Path.home() / "Library" / "Messages" / "chat.db"

# Open in read-only mode
conn = sqlite3.connect(f"file:{db_path}?mode=ro", uri=True)
cursor = conn.cursor()

# Query messages
cursor.execute("""
    SELECT text, date, is_from_me
    FROM message
    WHERE handle_id = ?
    ORDER BY date DESC
    LIMIT 50
""", (handle_id,))

messages = cursor.fetchall()
```

## Granting Full Disk Access

If using direct database access:

1. Open **System Preferences** > **Security & Privacy**
2. Go to **Privacy** tab
3. Select **Full Disk Access** in the left sidebar
4. Click the lock to make changes
5. Click **+** and add:
   - Terminal (if running from terminal)
   - Python (if running directly)
   - Your IDE (if running from VS Code, PyCharm, etc.)
6. Restart the application after granting access

## Database Schema

The Messages database has several important tables:

- `message` - Contains message text and metadata
- `handle` - Contains contact information (phone/email)
- `chat` - Contains conversation information
- `chat_message_join` - Links messages to conversations
- `attachment` - Contains file attachments

## Troubleshooting

### Permission Denied

- **"Not authorized to send Apple events"**: Grant Terminal access in System Preferences
- **"Messages doesn't understand"**: Ensure Messages app is installed and running
- **Database locked**: Close Messages app when accessing database directly

### macOS Version Differences

- Database schema may vary slightly between macOS versions
- Test queries on your specific macOS version
- Dates in the database use Apple's epoch (2001-01-01)

### Converting Apple Dates

Messages database uses seconds since 2001-01-01:

```python
from datetime import datetime, timedelta

def convert_apple_date(apple_date):
    # Apple epoch: 2001-01-01
    apple_epoch = datetime(2001, 1, 1)
    return apple_epoch + timedelta(seconds=apple_date)
```

## Security and Privacy Notes

- **Local Access Only**: Messages data never leaves your machine
- **Read-Only**: These tools only read messages, never send or modify
- **Sensitive Data**: iMessage contains sensitive personal communications
- **Access Logs**: macOS logs automation access in Console.app
- **Full Disk Access**: Be cautious granting this permission

## Alternative Approach: Export Messages

For occasional use:

1. Open Messages app
2. Select conversation
3. File > Export Chat
4. Save as text file
5. Parse the exported file

## Future Enhancements

Potential improvements for production use:

1. Direct SQLite database access
2. Full-text search using SQLite FTS
3. Attachment handling
4. Group message support
5. Message reactions and effects
6. Contact name resolution using Contacts.app

## References

- [Messages Database Structure](https://www.theiphonewiki.com/wiki/Messages)
- [AppleScript Language Guide](https://developer.apple.com/library/archive/documentation/AppleScript/Conceptual/AppleScriptLangGuide/)
- macOS Privacy Controls Documentation
