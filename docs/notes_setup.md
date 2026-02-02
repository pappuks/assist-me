# Mac Notes Setup Guide (macOS Only)

This guide explains how to set up Mac Notes integration for the Assist-Me MCP server.

⚠️ **Important**: Mac Notes tools only work on macOS systems.

## Prerequisites

- macOS operating system
- Notes app installed
- Terminal/Python access to Notes (see permissions below)

## Approach

The Notes tools use AppleScript to interact with the Notes app on macOS. This provides read-only access to your notes.

## Step 1: Grant Terminal Access

macOS requires permission for Terminal to control the Notes app:

1. Open **System Preferences/Settings**
2. Go to **Security & Privacy** > **Privacy**
3. Select **Automation** in the left sidebar
4. Find **Terminal** (or your terminal app) in the list
5. Check the box next to **Notes** to grant access

### First Run

The first time you use a Notes tool:

1. macOS will show a permission dialog
2. Click **OK** to allow Terminal to control Notes
3. The permission is saved for future use

## Step 2: No Additional Configuration Required

Notes access doesn't require API keys or OAuth. The tools work directly with your local Notes app.

## Available Tools

- `notes_list_notes` - List notes from all or specific folder
- `notes_read_note` - Read content of a specific note
- `notes_search_notes` - Search notes by title or content
- `notes_list_folders` - List all folders
- `notes_check_availability` - Check if Notes tools are available

## Usage Examples

### Check Availability
```python
await notes_check_availability()
# Returns platform info and requirements
```

### List All Notes
```python
# List recent 20 notes from all folders
await notes_list_notes(limit=20)

# List notes from specific folder
await notes_list_notes(folder="Work", limit=50)
```

### List Folders
```python
await notes_list_folders()
# Returns all note folders
```

### Read a Note
```python
await notes_read_note(note_id="x-coredata://...")
# Returns note content and metadata
```

### Search Notes
```python
await notes_search_notes(query="meeting", limit=20)
# Returns notes containing "meeting"
```

## Current Limitations

The current AppleScript implementation has limitations:

1. **Basic Output**: AppleScript returns raw text that needs parsing
2. **Performance**: Slower than direct database access
3. **Note IDs**: AppleScript note IDs are x-coredata:// URLs (not user-friendly)

## Advanced Implementation: Direct Database Access

For production use, consider accessing the Notes database directly:

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
ZICCLOUDSYNCINGOBJECT  -- All syncing objects (base table)
ZICNOTEDATA           -- Note content (HTML/text)
ZICNOTE               -- Note metadata
ZICFOLDER             -- Folders/accounts

-- Important columns in ZICNOTE:
- ZTITLE              -- Note title
- ZMODIFICATIONDATE   -- Last modified (Apple timestamp)
- ZCREATIONDATE       -- Created date
- ZFOLDER             -- Foreign key to ZICFOLDER
- ZNOTEDATA           -- Foreign key to ZICNOTEDATA

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

### Permission Issues

- **"Notes doesn't understand"**: Grant Terminal access in System Preferences > Privacy > Automation
- **"Operation not permitted"**: Grant Full Disk Access for database access
- **AppleScript errors**: Ensure Notes app is installed and updated

### Database Issues

- **Database locked**: Close Notes app when accessing database in read-only mode
- **Corrupt database**: Check Console.app for errors, may need to rebuild Notes
- **Schema changes**: Database schema may vary between macOS versions

### Content Extraction

- **Garbled text**: Ensure proper decompression of ZDATA field
- **Missing content**: Some notes may be synced and not fully downloaded
- **HTML parsing**: Use BeautifulSoup for robust HTML parsing

## Security and Privacy Notes

- **Local Access Only**: Notes data never leaves your machine
- **Read-Only**: These tools only read notes, never modify
- **Sensitive Data**: Notes may contain passwords, personal info
- **Full Disk Access**: Be cautious granting this permission
- **iCloud Sync**: Some notes may be cloud-only placeholders

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

## Alternative: Export Notes

For occasional use:

1. Open Notes app
2. Select note(s)
3. File > Export as PDF/HTML
4. Process exported files

## Future Enhancements

Potential improvements for production use:

1. Direct SQLite database access
2. Full-text search using FTS
3. Attachment extraction (images, PDFs)
4. Tag support
5. Checklist parsing
6. Table extraction
7. Drawing/sketch handling

## Example Full Implementation

```python
import sqlite3
import gzip
from pathlib import Path
from datetime import datetime, timedelta
from bs4 import BeautifulSoup

class NotesReader:
    def __init__(self):
        self.db_path = Path.home() / "Library" / "Group Containers" / \
                       "group.com.apple.notes" / "NoteStore.sqlite"

    def convert_date(self, apple_date):
        epoch = datetime(2001, 1, 1)
        return epoch + timedelta(seconds=apple_date)

    def list_notes(self, limit=50):
        conn = sqlite3.connect(f"file:{self.db_path}?mode=ro", uri=True)
        cursor = conn.cursor()

        cursor.execute("""
            SELECT
                note.Z_PK,
                note.ZTITLE,
                note.ZMODIFICATIONDATE,
                folder.ZTITLE2 as folder
            FROM ZICCLOUDSYNCINGOBJECT note
            LEFT JOIN ZICCLOUDSYNCINGOBJECT folder
                ON note.ZFOLDER = folder.Z_PK
            WHERE note.ZTITLE IS NOT NULL
            ORDER BY note.ZMODIFICATIONDATE DESC
            LIMIT ?
        """, (limit,))

        notes = []
        for row in cursor.fetchall():
            notes.append({
                'id': row[0],
                'title': row[1],
                'modified': self.convert_date(row[2]),
                'folder': row[3]
            })

        return notes

    def get_note_content(self, note_id):
        conn = sqlite3.connect(f"file:{self.db_path}?mode=ro", uri=True)
        cursor = conn.cursor()

        cursor.execute("""
            SELECT
                note.ZTITLE,
                data.ZDATA
            FROM ZICCLOUDSYNCINGOBJECT note
            JOIN ZICNOTEDATA data ON note.ZNOTEDATA = data.Z_PK
            WHERE note.Z_PK = ?
        """, (note_id,))

        row = cursor.fetchone()
        if row:
            title, compressed_data = row
            html_content = gzip.decompress(compressed_data).decode('utf-8')
            soup = BeautifulSoup(html_content, 'html.parser')
            text = soup.get_text()
            return {'title': title, 'content': text}

        return None
```

## References

- [Notes Database Structure](https://github.com/threeplanetssoftware/apple_cloud_notes_parser)
- [AppleScript Notes Dictionary](https://developer.apple.com/library/archive/documentation/AppleScript/)
- macOS Security & Privacy Documentation
- [SQLite Documentation](https://www.sqlite.org/docs.html)
