# iMessage Setup Guide (macOS Only)

This guide explains how to set up iMessage integration for the Assist-Me MCP server.

⚠️ **Important**: iMessage tools only work on macOS systems.

## Prerequisites

- macOS operating system
- Messages app installed and configured with message history
- Full Disk Access permission for your Terminal or Python environment

## Approach

The iMessage tools use **direct SQLite database access** to read Messages data on macOS. This provides reliable, read-only access to your messages with full search functionality and better performance than AppleScript.

**Database Location**: `~/Library/Messages/chat.db`

## Step 1: Grant Full Disk Access

macOS requires Full Disk Access permission to read the Messages database:

1. Open **System Settings** (or **System Preferences** on older macOS)
2. Go to **Privacy & Security** > **Privacy**
3. Select **Full Disk Access** in the left sidebar
4. Click the **lock icon** at the bottom to make changes (you'll need to authenticate)
5. Click the **+** button
6. Add your application:
   - **Terminal** (if running from terminal)
   - **Python** or **Python.app** (if running directly)
   - **VS Code** or your IDE (if running from an IDE)
7. **Restart** the application after granting access

### Verifying Access

After granting Full Disk Access, you can verify it works by running:

```bash
sqlite3 ~/Library/Messages/chat.db "SELECT COUNT(*) FROM message"
```

If this returns a number, access is working correctly. If you see "unable to open database file", the permission hasn't been granted yet or the application needs to be restarted.

## Step 2: No Additional Configuration Required

Unlike cloud services, iMessage access doesn't require API keys or OAuth. The tools work directly with your local Messages database.

## Available Tools

The iMessage tools now use direct database access for reliable functionality:

- `imessage_check_availability` - Check if iMessage tools are available and verify permissions
- `imessage_list_recent_conversations` - List recent conversations with last message preview
- `imessage_get_contact_list` - Get all contacts you've messaged with
- `imessage_read_messages` - Read messages from a specific contact or phone number
- `imessage_search_messages` - Search for messages containing specific text (fully functional)

## Usage Examples

### Check Availability and Permissions
```python
await imessage_check_availability()
# Returns:
# {
#   "available": true/false,
#   "platform": "Darwin",
#   "database_path": "/Users/you/Library/Messages/chat.db",
#   "error": "...", (if not accessible)
#   "setup_instructions": "..." (if permissions needed)
# }
```

### List Recent Conversations
```python
await imessage_list_recent_conversations(limit=20)
# Returns list of recent contacts with:
# - Contact identifier (phone/email)
# - Last message preview
# - Last message date
# - Total message count
```

### Get All Contacts
```python
await imessage_get_contact_list()
# Returns all contacts you've messaged with, sorted by most recent
```

### Read Messages from a Contact
```python
await imessage_read_messages(
    contact="+15551234567",  # Use full phone number or email
    limit=50
)
# Returns messages in chronological order with:
# - Message text
# - Timestamp
# - Sender (you or the contact)
# - Attachment indicator
```

### Search Messages
```python
# Search all messages
await imessage_search_messages(
    query="meeting tomorrow",
    limit=50
)

# Search messages from specific contact
await imessage_search_messages(
    query="meeting tomorrow",
    contact="+15551234567",
    limit=50
)
# Returns matching messages with full context
```

## Key Features

The direct database implementation provides:

1. **Full Functionality**: All features work reliably
2. **Full-Text Search**: Search across all messages or within specific conversations
3. **Better Performance**: Direct SQL queries are fast and efficient
4. **Rich Metadata**: Access to timestamps, attachments, message direction
5. **Contact Discovery**: List all contacts and find similar contact IDs
6. **Error Handling**: Clear error messages with setup instructions

## Database Schema Reference

The Messages database uses these main tables:

- `message` - Contains message text, timestamps, and metadata
- `handle` - Contains contact information (phone numbers/emails)
- `chat` - Contains conversation information (including group chats)
- `chat_message_join` - Links messages to conversations
- `attachment` - Contains file attachments and media

### Useful Database Fields

From the `message` table:
- `text` - Message content
- `date` - Timestamp (nanoseconds since Apple epoch: 2001-01-01)
- `is_from_me` - Boolean indicating if you sent the message
- `cache_has_attachments` - Boolean indicating if message has attachments
- `handle_id` - Foreign key to the contact

From the `handle` table:
- `id` - Contact identifier (phone number or email)
- `service` - Service type (iMessage, SMS, etc.)

## Troubleshooting

### Permission Denied Errors

**Error: "unable to open database file"**
- You need to grant Full Disk Access permission (see Step 1 above)
- Make sure you've restarted the application after granting permission
- Verify the Messages app has created message history

**Error: "Database not found"**
- Ensure Messages app is installed and has been opened at least once
- Check that you have message history in the Messages app

**Error: "Database locked"**
- The Messages app may have the database locked
- This should not normally happen with read-only access
- Try closing and reopening the Messages app

### Contact Identifier Format

**Phone Numbers**: Must use the exact format stored in the database
- Usually includes country code: `+15551234567`
- Use `imessage_get_contact_list()` to see the exact format
- The `imessage_read_messages` tool will suggest similar contacts if not found

**Email Addresses**: Use the exact email address as stored

**Tip**: Use `imessage_list_recent_conversations()` to see recent contacts with their exact identifiers

### No Messages Returned

**No results from search or read:**
- Double-check the contact identifier format (use exact phone/email from database)
- Use `imessage_get_contact_list()` to find the correct identifier
- Ensure the contact actually has message history

### macOS Version Differences

- Database schema is generally consistent across recent macOS versions
- Dates in the database use Apple's epoch (2001-01-01) stored as nanoseconds
- The tools automatically handle date conversion

## Security and Privacy Notes

- **Local Access Only**: Messages data never leaves your machine
- **Read-Only Access**: These tools only read messages, never send or modify
- **Sensitive Data**: iMessage contains sensitive personal communications
- **Full Disk Access**: Be cautious granting this permission - it provides access to all your files
- **Recommended**: Only grant Full Disk Access to trusted applications
- **Audit**: Check what apps have Full Disk Access periodically in System Settings

## Current Limitations

1. **Read-Only**: Cannot send messages or modify existing messages
2. **Attachments**: Can detect attachments but doesn't extract attachment content
3. **Group Chats**: Currently treats group chats individually (by contact ID)
4. **Reactions**: Message reactions are stored as separate messages
5. **Contact Names**: Shows phone/email identifiers, not contact names from Contacts.app

## Alternative Approach: Export Messages

For one-time or occasional use without granting Full Disk Access:

1. Open Messages app
2. Select conversation
3. File > Export Chat
4. Save as text file
5. Read the exported file directly

This approach doesn't require Full Disk Access but is manual and limited.

## Future Enhancement Ideas

Potential improvements for future versions:

1. Attachment content extraction
2. Group message thread reconstruction
3. Contact name resolution via Contacts.app
4. Message reaction parsing
5. Full-text search using SQLite FTS5
6. Date range filtering
7. Message statistics and analytics

## References

- [Messages Database Structure](https://www.theiphonewiki.com/wiki/Messages)
- [AppleScript Language Guide](https://developer.apple.com/library/archive/documentation/AppleScript/Conceptual/AppleScriptLangGuide/)
- macOS Privacy Controls Documentation
