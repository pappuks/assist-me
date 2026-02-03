# Mac Notes Setup Guide (macOS Only)

This guide explains how to set up Mac Notes integration for the Assist-Me MCP server.

⚠️ **Important**: Mac Notes tools only work on macOS systems.

## Prerequisites

- macOS operating system
- Notes app installed and configured with notes
- Full Disk Access permission for your Terminal or IDE

## Approach

The Notes tools use **direct SQLite database access** to read Notes data on macOS. This provides reliable, read-only access to your notes with full functionality and better performance than AppleScript.

**Database Location**: `~/Library/Group Containers/group.com.apple.notes/NoteStore.sqlite`

## Step 1: Grant Full Disk Access

macOS requires Full Disk Access permission to read the Notes database:

1. Open **System Settings** (or **System Preferences** on older macOS)
2. Go to **Privacy & Security** > **Privacy**
3. Select **Full Disk Access** in the left sidebar
4. Click the **lock icon** at the bottom to make changes (you'll need to authenticate)
5. Click the **+** button
6. Add your application:
   - **Terminal** (if running from terminal)
   - **Visual Studio Code** or **Code** (if running from VS Code)
   - **Python** or **Python.app** (if running directly)
7. **Restart** the application after granting access

### Verifying Access

After granting Full Disk Access, you can verify it works by running:

```bash
sqlite3 ~/Library/Group\ Containers/group.com.apple.notes/NoteStore.sqlite "SELECT COUNT(*) FROM ZICCLOUDSYNCINGOBJECT WHERE ZTITLE IS NOT NULL"
```

If this returns a number, access is working correctly. If you see "unable to open database file", the permission hasn't been granted yet or the application needs to be restarted.

## Step 2: No Additional Configuration Required

Unlike cloud services, Notes access doesn't require API keys or OAuth. The tools work directly with your local Notes database.

## Available Tools

The Notes tools now use direct database access for reliable functionality:

- `notes_check_availability` - Check if Notes tools are available and verify permissions
- `notes_list_folders` - List all folders with note counts
- `notes_list_notes` - List notes with preview snippets and metadata
- `notes_read_note` - Read full content of a specific note (with HTML parsing)
- `notes_search_notes` - Search notes by title or content with context previews

## Usage Examples

### Check Availability and Permissions
```python
await notes_check_availability()
# Returns:
# {
#   "available": true/false,
#   "platform": "Darwin",
#   "database_path": "/Users/you/Library/Group Containers/group.com.apple.notes/NoteStore.sqlite",
#   "error": "...", (if not accessible)
#   "setup_instructions": "..." (if permissions needed)
# }
```

### List Folders
```python
await notes_list_folders()
# Returns all folders with note counts:
# [
#   {"id": 1, "name": "Notes", "note_count": 150},
#   {"id": 2, "name": "Work", "note_count": 45}
# ]
```

### List All Notes
```python
# List recent 20 notes from all folders
await notes_list_notes(limit=20)

# List notes from specific folder
await notes_list_notes(folder="Work", limit=50)

# Returns:
# [
#   {
#     "id": 123,
#     "title": "Meeting Notes",
#     "folder": "Work",
#     "modified": "2024-01-15T10:30:00",
#     "preview": "Discussed project timeline..."
#   }
# ]
```

### Read a Note
```python
await notes_read_note(note_id=123)
# Returns note with full content (HTML converted to plain text):
# {
#   "id": 123,
#   "title": "Meeting Notes",
#   "content": "Full plain text content of the note...",
#   "folder": "Work",
#   "modified": "2024-01-15T10:30:00",
#   "created": "2024-01-14T09:00:00"
# }
```

### Search Notes
```python
# Search all notes
await notes_search_notes(query="meeting", limit=20)

# Returns matching notes with context:
# [
#   {
#     "id": 123,
#     "title": "Meeting Notes",
#     "folder": "Work",
#     "modified": "2024-01-15T10:30:00",
#     "preview": "...discussed the meeting agenda and..."
#   }
# ]
```

## Key Features

The direct database implementation provides:

1. **Full Functionality**: All features work reliably without AppleScript limitations
2. **Content Extraction**: Automatic gzip decompression and HTML-to-text conversion
3. **Better Performance**: Direct SQL queries are fast and efficient
4. **Rich Metadata**: Access to titles, folders, creation/modification dates, snippets
5. **Context-Aware Search**: Search results include relevant context around matches
6. **Error Handling**: Clear error messages with setup instructions

## Implementation Details: Direct Database Access

The Notes tools use direct SQLite database access for optimal performance and reliability:

### Database Locations

Notes data is stored in several SQLite databases:

```bash
# Modern Notes (macOS 10.14+)
~/Library/Group Containers/group.com.apple.notes/

# Files:
- NoteStore.sqlite         # Main database with notes
- NoteStore.sqlite-wal     # Write-ahead log
- NoteStore.sqlite-shm     # Shared memory

# Older Notes
~/Library/Containers/com.apple.Notes/Data/Library/Notes/
```

### Granting Full Disk Access

To access the Notes database:

1. Open **System Preferences** > **Security & Privacy**
2. Go to **Privacy** tab
3. Select **Full Disk Access**
4. Click **+** and add Terminal/Python/your IDE
5. Restart the application

### Database Schema (Simplified)

Key tables in NoteStore.sqlite:

```sql
-- Main tables
ZICCLOUDSYNCINGOBJECT  -- All syncing objects (base table with entity types)
ZICNOTEDATA           -- Note content (gzipped HTML)
Z_PRIMARYKEY          -- Entity type definitions

-- Entity Types (Z_ENT values in ZICCLOUDSYNCINGOBJECT):
Z_ENT = 12  -- ICNote (actual notes)
Z_ENT = 15  -- ICFolder (folders/containers)
Z_ENT = 5   -- ICAttachment (file attachments)
Z_ENT = 6   -- ICAttachmentPreviewImage (attachment previews)
Z_ENT = 11  -- ICMedia (media files)

-- Important columns for notes (Z_ENT = 12):
- ZTITLE1             -- Note title
- ZMODIFICATIONDATE1  -- Last modified (Apple timestamp, seconds since 2001-01-01)
- ZCREATIONDATE1      -- Created date
- ZFOLDER             -- Foreign key to folder (Z_ENT = 15)
- ZNOTEDATA           -- Foreign key to ZICNOTEDATA
- ZSNIPPET            -- Plain text preview/snippet

-- Important columns in ZICNOTEDATA:
- ZDATA               -- Note content (gzipped HTML)
```

### Example SQL Queries

```sql
-- List all notes with titles
SELECT
    note.Z_PK as id,
    note.ZTITLE as title,
    note.ZMODIFICATIONDATE as modified,
    folder.ZTITLE2 as folder_name
FROM ZICCLOUDSYNCINGOBJECT note
LEFT JOIN ZICCLOUDSYNCINGOBJECT folder ON note.ZFOLDER = folder.Z_PK
WHERE note.ZTITLE IS NOT NULL
ORDER BY note.ZMODIFICATIONDATE DESC
LIMIT 50;

-- Search notes by title
SELECT Z_PK, ZTITLE, ZMODIFICATIONDATE
FROM ZICCLOUDSYNCINGOBJECT
WHERE ZTITLE LIKE '%search term%'
ORDER BY ZMODIFICATIONDATE DESC;

-- Get note content (requires decompression)
SELECT
    note.ZTITLE,
    data.ZDATA as content_compressed
FROM ZICCLOUDSYNCINGOBJECT note
JOIN ZICNOTEDATA data ON note.ZNOTEDATA = data.Z_PK
WHERE note.Z_PK = ?;
```

### Content Decompression

Note content in ZICNOTEDATA.ZDATA is gzip-compressed:

```python
import gzip
import sqlite3
from pathlib import Path

def get_note_content(note_id):
    db_path = Path.home() / "Library" / "Group Containers" / \
              "group.com.apple.notes" / "NoteStore.sqlite"

    conn = sqlite3.connect(f"file:{db_path}?mode=ro", uri=True)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT data.ZDATA
        FROM ZICCLOUDSYNCINGOBJECT note
        JOIN ZICNOTEDATA data ON note.ZNOTEDATA = data.Z_PK
        WHERE note.Z_PK = ?
    """, (note_id,))

    compressed_data = cursor.fetchone()[0]

    # Decompress
    if compressed_data:
        decompressed = gzip.decompress(compressed_data)
        # Parse HTML to extract text
        return decompressed.decode('utf-8')

    return None
```

### Date Conversion

Notes uses Apple's Core Data timestamp (seconds since 2001-01-01):

```python
from datetime import datetime, timedelta

def convert_apple_date(apple_timestamp):
    # Apple epoch: January 1, 2001
    apple_epoch = datetime(2001, 1, 1)
    return apple_epoch + timedelta(seconds=apple_timestamp)

# Example:
# If ZMODIFICATIONDATE = 697896000
# convert_apple_date(697896000) => 2023-02-09 16:00:00
```

## Parsing HTML Content

Note content is stored as HTML. To extract plain text:

```python
from html.parser import HTMLParser
from io import StringIO

class HTMLTextExtractor(HTMLParser):
    def __init__(self):
        super().__init__()
        self.text = StringIO()

    def handle_data(self, data):
        self.text.write(data)

    def get_text(self):
        return self.text.getvalue()

def extract_text_from_html(html_content):
    extractor = HTMLTextExtractor()
    extractor.feed(html_content)
    return extractor.get_text()
```

## Using Python Libraries

### For Database Access

```bash
pip install sqlite3  # Built-in to Python
```

### For HTML Parsing

```bash
pip install beautifulsoup4 lxml
```

Example:
```python
from bs4 import BeautifulSoup

def parse_note_html(html_content):
    soup = BeautifulSoup(html_content, 'lxml')
    # Extract text
    text = soup.get_text()
    # Extract images
    images = soup.find_all('img')
    return text, images
```

## Troubleshooting

### Permission Denied Errors

**Error: "unable to open database file"**
- You need to grant Full Disk Access permission (see Step 1 above)
- Make sure you've restarted the application after granting permission
- Verify the Notes app has created notes (database won't exist without notes)

**Error: "Database not found"**
- Ensure Notes app is installed and has been opened at least once
- Check that you have notes in the Notes app
- Database location: `~/Library/Group Containers/group.com.apple.notes/NoteStore.sqlite`

**Error: "Database locked"**
- The Notes app may have the database locked
- This should not normally happen with read-only access
- Try closing and reopening the Notes app

### Content Issues

**No content returned for a note:**
- Some notes may be iCloud-synced placeholders without full content downloaded
- Check if the note has content in the Notes app
- The tool will fall back to the snippet field if full content is unavailable

**Garbled or incomplete text:**
- Ensure the gzip decompression is working properly
- Some older notes may have different encoding
- Check if the note displays correctly in the Notes app

### Database Schema Differences

**Error: "no such column"**
- Database schema may vary slightly between macOS versions
- The implementation uses common fields (ZTITLE, ZSNIPPET, ZDATA)
- macOS 10.14+ uses the modern schema in Group Containers

## Security and Privacy Notes

- **Local Access Only**: Notes data never leaves your machine - all processing is local
- **Read-Only**: These tools only read notes, never send, modify, or delete
- **Sensitive Data**: Notes may contain passwords, personal information, private thoughts
- **Full Disk Access**: Be cautious granting this permission - it provides access to all your files
- **Recommended**: Only grant Full Disk Access to trusted applications (Terminal, VS Code, Python)
- **Audit**: Check what apps have Full Disk Access periodically in System Settings
- **iCloud Sync**: Notes synced to iCloud may be stored as placeholders locally

## Folder Organization

Notes are organized in folders/accounts:

```
On My Mac
  ├── Notes (default folder)
  ├── Work
  └── Personal

iCloud
  ├── Notes
  └── Archived
```

Use `notes_list_folders()` to see your folder structure.

## Current Limitations

The current implementation has some limitations:

1. **Read-Only**: Cannot create, modify, or delete notes
2. **Attachments**: Can detect attachments but doesn't extract attachment content (images, PDFs, files)
3. **Rich Formatting**: Converts to plain text, losing formatting like bold, italic, lists
4. **Tables**: Table structure is converted to plain text
5. **Drawings**: Sketch/drawing content is not extracted
6. **iCloud Sync**: Some notes may be placeholders if not fully synced to local storage

## Alternative Approach: Export Notes

For one-time or occasional use without granting Full Disk Access:

1. Open Notes app
2. Select note(s)
3. File > Export as PDF or HTML
4. Process the exported files directly

This approach doesn't require Full Disk Access but is manual and limited to individual notes.

## Future Enhancement Ideas

Potential improvements for future versions:

1. Attachment content extraction (images, PDFs, documents)
2. Preserve rich formatting (markdown conversion)
3. Checklist parsing and task tracking
4. Table structure preservation
5. Drawing/sketch image extraction
6. Full-text search using SQLite FTS5
7. Tag support (if Notes adds tagging in future macOS versions)
8. Folder hierarchy reconstruction
9. Shared notes detection

## Implementation Reference

The full implementation is available in `src/tools/notes.py`, which includes:

- Database connection handling with read-only mode
- Gzip decompression for note content
- HTML-to-text conversion
- Apple timestamp conversion (2001-01-01 epoch)
- Error handling and permission checking
- Search with context extraction

The implementation follows the same pattern as the iMessage tools (`src/tools/imessage.py`) for consistency.

## References

- [Apple Notes Database Structure](https://github.com/threeplanetssoftware/apple_cloud_notes_parser) - Detailed schema documentation
- [SQLite Documentation](https://www.sqlite.org/docs.html) - SQLite query reference
- macOS Privacy & Security Documentation - Full Disk Access setup
- Similar implementation: `docs/imessage_setup.md` - iMessage SQLite access guide
