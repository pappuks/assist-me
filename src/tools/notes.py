"""Mac Notes tools for MCP server (macOS only).

Uses direct SQLite database access to read Notes data on macOS.
This approach is more reliable than AppleScript and provides better functionality.

Note: Requires macOS and Full Disk Access permission for the application.
"""

import sqlite3
import platform
import gzip
import re
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Any, Optional
from mcp.server.fastmcp import FastMCP

# Try to import BeautifulSoup, fall back to basic parsing if not available
try:
    from bs4 import BeautifulSoup
    HAS_BS4 = True
except ImportError:
    HAS_BS4 = False


def _is_macos() -> bool:
    """Check if running on macOS."""
    return platform.system() == "Darwin"


def _get_notes_db_path() -> Path:
    """Get the path to the Notes database."""
    return Path.home() / "Library" / "Group Containers" / "group.com.apple.notes" / "NoteStore.sqlite"


def _check_db_access() -> tuple[bool, Optional[str]]:
    """Check if the Notes database is accessible.

    Returns:
        Tuple of (is_accessible, error_message)
    """
    if not _is_macos():
        return False, "Notes tools are only available on macOS"

    db_path = _get_notes_db_path()

    if not db_path.exists():
        return False, f"Notes database not found at {db_path}"

    try:
        # Try to open the database in read-only mode
        conn = sqlite3.connect(f"file:{db_path}?mode=ro", uri=True)
        conn.close()
        return True, None
    except sqlite3.OperationalError as e:
        if "unable to open database file" in str(e).lower():
            return False, (
                "Unable to access Notes database. Full Disk Access permission required.\n"
                "Grant access in: System Settings > Privacy & Security > Full Disk Access\n"
                "Add your terminal app, IDE, or Python to the list and restart the application."
            )
        return False, f"Database access error: {str(e)}"
    except Exception as e:
        return False, f"Unexpected error accessing database: {str(e)}"


def _convert_apple_timestamp(timestamp: float) -> str:
    """Convert Apple's Core Data timestamp to readable format.

    Args:
        timestamp: Apple timestamp in seconds since 2001-01-01

    Returns:
        ISO format datetime string
    """
    if timestamp == 0 or timestamp is None:
        return "Unknown"

    try:
        # Apple Core Data epoch is 2001-01-01
        apple_epoch = datetime(2001, 1, 1)
        dt = apple_epoch + timedelta(seconds=timestamp)
        return dt.isoformat()
    except (ValueError, OverflowError):
        return "Invalid date"


def _is_garbage_line(line: str) -> bool:
    """Check if a line looks like binary metadata/garbage.

    Args:
        line: Single line of text

    Returns:
        True if line appears to be garbage
    """
    stripped = line.strip()

    # Empty lines are ok
    if not stripped:
        return False

    # Very short lines with weird patterns like "! (" or "#("
    if len(stripped) <= 4 and ('(' in stripped or ')' in stripped):
        return True

    # Lines that are mostly non-ASCII or control characters
    ascii_chars = sum(1 for c in stripped if ord(c) < 128)
    if len(stripped) > 0 and ascii_chars / len(stripped) < 0.5:
        # More than half non-ASCII might be binary
        return True

    # Lines with repeated weird patterns
    if re.search(r'[^\w\s]{3,}', stripped):  # 3+ consecutive non-word/non-space chars
        # But allow URLs, emails, common punctuation
        if not any(pattern in stripped for pattern in ['http', 'mailto', '://', '@', '.']):
            return True

    return False


def _clean_text(text: str) -> str:
    """Clean text by removing control characters and extra whitespace.

    Args:
        text: Raw text string

    Returns:
        Cleaned text string
    """
    # Remove control characters (except newlines and tabs)
    text = re.sub(r'[\x00-\x08\x0B-\x0C\x0E-\x1F\x7F-\x9F]', '', text)

    # Remove zero-width characters and other unicode oddities
    text = re.sub(r'[\u200B-\u200D\uFEFF]', '', text)

    # Replace multiple whitespace with single space (but preserve newlines)
    text = re.sub(r'[ \t]+', ' ', text)

    # Split into lines and remove garbage
    # Be conservative - only remove obviously bad lines, don't stop early
    lines = text.split('\n')
    cleaned_lines = []
    garbage_count = 0

    for line in lines:
        if _is_garbage_line(line):
            garbage_count += 1
            # Only stop if we hit 10 consecutive garbage lines (very conservative)
            # This catches the binary metadata at the end but preserves content
            if garbage_count >= 10:
                break
            # Don't include the garbage line itself, just skip it
            continue
        else:
            garbage_count = 0
            # Keep all non-garbage lines, including empty ones (for paragraph breaks)
            cleaned_lines.append(line)

    text = '\n'.join(cleaned_lines)

    # Remove excessive newlines (more than 2 consecutive)
    text = re.sub(r'\n{3,}', '\n\n', text)

    return text.strip()


def _extract_text_from_html(html_content: str) -> str:
    """Extract plain text from Notes content.

    Notes stores content as plain text followed by binary metadata.
    This function extracts the meaningful text and removes metadata.

    Args:
        html_content: Decompressed content from Notes database

    Returns:
        Plain text content with formatting cleaned up
    """
    try:
        # Apple Notes format is plain text followed by metadata
        # Look for the start of binary metadata (the repeated J>Q&ggJ9;Wk.h pattern)
        # This is more reliable than trying to detect individual garbage lines
        binary_marker = 'J>Q&gg'  # Distinctive pattern in Notes metadata

        # Find where the binary metadata starts
        content_end = len(html_content)
        pos = html_content.find(binary_marker)
        if pos > 0:
            content_end = pos

        # Also check for other metadata markers
        other_markers = [
            '\x08\x00\x12',  # Binary protobuf-like markers
            'com.apple.notes.inlinetextattachment',  # Inline attachment metadata
        ]

        for marker in other_markers:
            marker_pos = html_content.find(marker)
            if marker_pos > 0 and marker_pos < content_end:
                content_end = marker_pos

        # Extract just the content part (before metadata)
        text = html_content[:content_end]

        # If it looks like HTML (has tags), parse it
        if '<' in text and '>' in text:
            if HAS_BS4:
                soup = BeautifulSoup(text, 'html.parser')
                for element in soup(['style', 'script', 'meta', 'link']):
                    element.decompose()
                text = soup.get_text(separator='\n')
            else:
                # Basic HTML stripping
                text = re.sub(r'<[^>]+>', '', text)
                text = text.replace('&nbsp;', ' ')
                text = text.replace('&lt;', '<')
                text = text.replace('&gt;', '>')
                text = text.replace('&amp;', '&')
                text = text.replace('&quot;', '"')

        return _clean_text(text)
    except Exception as e:
        # If parsing fails completely, try basic cleaning
        return _clean_text(html_content)


def _execute_query(query: str, params: tuple = ()) -> List[tuple]:
    """Execute a query on the Notes database.

    Args:
        query: SQL query to execute
        params: Query parameters

    Returns:
        List of result tuples

    Raises:
        RuntimeError: If database access fails
    """
    accessible, error = _check_db_access()
    if not accessible:
        raise RuntimeError(error)

    db_path = _get_notes_db_path()

    try:
        conn = sqlite3.connect(f"file:{db_path}?mode=ro", uri=True)
        cursor = conn.cursor()
        cursor.execute(query, params)
        results = cursor.fetchall()
        conn.close()
        return results
    except Exception as e:
        raise RuntimeError(f"Database query failed: {str(e)}")


def register_notes_tools(mcp: FastMCP):
    """Register Mac Notes-related tools with the MCP server.

    Note: These tools only work on macOS and require Full Disk Access permission.
    """

    @mcp.tool()
    async def notes_check_availability() -> Dict[str, Any]:
        """Check if Mac Notes tools are available on this system.

        Returns:
            Availability status, database path, and setup instructions
        """
        is_available, error = _check_db_access()
        db_path = _get_notes_db_path()

        result = {
            "available": is_available,
            "platform": platform.system(),
            "database_path": str(db_path),
        }

        if not is_available:
            result["error"] = error
            result["setup_instructions"] = (
                "1. Open System Settings > Privacy & Security > Full Disk Access\n"
                "2. Click the + button and add your application (Terminal, VS Code, Python)\n"
                "3. Restart the application after granting permission\n"
                "4. Verify by running: sqlite3 ~/Library/Group\\ Containers/group.com.apple.notes/NoteStore.sqlite 'SELECT COUNT(*) FROM ZICCLOUDSYNCINGOBJECT'"
            )

        return result

    @mcp.tool()
    async def notes_list_folders() -> List[Dict[str, Any]]:
        """List all folders in Mac Notes app.

        Returns:
            List of folders with id, name, and note count
        """
        try:
            query = """
                SELECT
                    Z_PK as id,
                    ZTITLE2 as name,
                    (SELECT COUNT(*)
                     FROM ZICCLOUDSYNCINGOBJECT note
                     WHERE note.ZFOLDER = folder.Z_PK AND note.Z_ENT = 12) as note_count
                FROM ZICCLOUDSYNCINGOBJECT folder
                WHERE Z_ENT = 15
                ORDER BY ZTITLE2
            """

            results = _execute_query(query)

            folders = []
            for row in results:
                folders.append({
                    "id": row[0],
                    "name": row[1],
                    "note_count": row[2]
                })

            return folders

        except Exception as e:
            return [{
                "error": f"Failed to list folders: {str(e)}",
                "suggestion": "Ensure Full Disk Access is granted. See notes_check_availability for setup."
            }]

    @mcp.tool()
    async def notes_list_notes(
        folder: Optional[str] = None,
        limit: int = 20,
    ) -> List[Dict[str, Any]]:
        """List notes from Mac Notes app.

        Args:
            folder: Folder name to filter by (optional)
            limit: Maximum number of notes to return (default: 20)

        Returns:
            List of notes with id, title, folder, modification date, and preview
        """
        try:
            if folder:
                query = """
                    SELECT
                        note.Z_PK as id,
                        note.ZTITLE1 as title,
                        folder.ZTITLE2 as folder_name,
                        note.ZMODIFICATIONDATE1 as modified,
                        note.ZSNIPPET as snippet
                    FROM ZICCLOUDSYNCINGOBJECT note
                    LEFT JOIN ZICCLOUDSYNCINGOBJECT folder ON note.ZFOLDER = folder.Z_PK
                    WHERE note.Z_ENT = 12
                      AND folder.ZTITLE2 = ?
                    ORDER BY note.ZMODIFICATIONDATE1 DESC
                    LIMIT ?
                """
                results = _execute_query(query, (folder, limit))
            else:
                query = """
                    SELECT
                        note.Z_PK as id,
                        note.ZTITLE1 as title,
                        folder.ZTITLE2 as folder_name,
                        note.ZMODIFICATIONDATE1 as modified,
                        note.ZSNIPPET as snippet
                    FROM ZICCLOUDSYNCINGOBJECT note
                    LEFT JOIN ZICCLOUDSYNCINGOBJECT folder ON note.ZFOLDER = folder.Z_PK
                    WHERE note.Z_ENT = 12
                    ORDER BY note.ZMODIFICATIONDATE1 DESC
                    LIMIT ?
                """
                results = _execute_query(query, (limit,))

            notes = []
            for row in results:
                notes.append({
                    "id": row[0],
                    "title": row[1],
                    "folder": row[2] or "Unknown",
                    "modified": _convert_apple_timestamp(row[3]),
                    "preview": row[4][:200] if row[4] else ""
                })

            return notes

        except Exception as e:
            return [{
                "error": f"Failed to list notes: {str(e)}",
                "suggestion": "Ensure Full Disk Access is granted. See notes_check_availability for setup."
            }]

    @mcp.tool()
    async def notes_read_note(note_id: int) -> Dict[str, Any]:
        """Read the content of a specific note.

        Args:
            note_id: Note ID (from notes_list_notes)

        Returns:
            Note content with title, body (plain text), folder, and metadata
        """
        try:
            query = """
                SELECT
                    note.ZTITLE1 as title,
                    note.ZSNIPPET as snippet,
                    folder.ZTITLE2 as folder_name,
                    note.ZMODIFICATIONDATE1 as modified,
                    note.ZCREATIONDATE1 as created,
                    data.ZDATA as content_data
                FROM ZICCLOUDSYNCINGOBJECT note
                LEFT JOIN ZICCLOUDSYNCINGOBJECT folder ON note.ZFOLDER = folder.Z_PK
                LEFT JOIN ZICNOTEDATA data ON note.ZNOTEDATA = data.Z_PK
                WHERE note.Z_PK = ? AND note.Z_ENT = 12
            """

            results = _execute_query(query, (note_id,))

            if not results:
                return {
                    "error": f"Note with id {note_id} not found",
                    "suggestion": "Use notes_list_notes to find valid note IDs"
                }

            row = results[0]
            title = row[0]
            snippet = row[1]
            folder = row[2] or "Unknown"
            modified = _convert_apple_timestamp(row[3])
            created = _convert_apple_timestamp(row[4])
            content_data = row[5]

            # Extract note content
            content = ""
            if content_data:
                try:
                    # Note content is gzip-compressed
                    decompressed = gzip.decompress(content_data)
                    html_content = decompressed.decode('utf-8', errors='ignore')
                    # Extract plain text from HTML
                    content = _extract_text_from_html(html_content)

                    # Only fall back to snippet if extraction completely failed
                    # (snippet is often truncated, so prefer full extraction)
                    if not content or len(content) < 5:
                        if snippet:
                            content = snippet
                except Exception as e:
                    content = f"Failed to decompress content: {str(e)}"
                    # Fall back to snippet if available
                    if snippet:
                        content = snippet
            elif snippet:
                content = snippet

            # If content is still empty, provide a helpful message
            if not content:
                content = "[Note appears to be empty or content could not be extracted]"

            return {
                "id": note_id,
                "title": title,
                "content": content,
                "folder": folder,
                "modified": modified,
                "created": created
            }

        except Exception as e:
            return {
                "error": f"Failed to read note: {str(e)}",
                "suggestion": "Ensure Full Disk Access is granted. See notes_check_availability for setup."
            }

    @mcp.tool()
    async def notes_search_notes(
        query: str,
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        """Search notes by title or content.

        Args:
            query: Search query (case-insensitive)
            limit: Maximum number of results (default: 20)

        Returns:
            List of matching notes with id, title, folder, and preview
        """
        try:
            sql_query = """
                SELECT
                    note.Z_PK as id,
                    note.ZTITLE1 as title,
                    folder.ZTITLE2 as folder_name,
                    note.ZMODIFICATIONDATE1 as modified,
                    note.ZSNIPPET as snippet
                FROM ZICCLOUDSYNCINGOBJECT note
                LEFT JOIN ZICCLOUDSYNCINGOBJECT folder ON note.ZFOLDER = folder.Z_PK
                WHERE note.Z_ENT = 12
                  AND (note.ZTITLE1 LIKE ? OR note.ZSNIPPET LIKE ?)
                ORDER BY note.ZMODIFICATIONDATE1 DESC
                LIMIT ?
            """

            search_pattern = f"%{query}%"
            results = _execute_query(sql_query, (search_pattern, search_pattern, limit))

            notes = []
            for row in results:
                # Find the matching snippet
                snippet = row[4] or ""
                title = row[1]

                # Try to extract context around the match
                preview = ""
                if query.lower() in snippet.lower():
                    # Find the match position and extract context
                    pos = snippet.lower().find(query.lower())
                    start = max(0, pos - 100)
                    end = min(len(snippet), pos + len(query) + 100)
                    preview = "..." + snippet[start:end] + "..."
                elif snippet:
                    preview = snippet[:200]

                notes.append({
                    "id": row[0],
                    "title": title,
                    "folder": row[2] or "Unknown",
                    "modified": _convert_apple_timestamp(row[3]),
                    "preview": preview
                })

            return notes

        except Exception as e:
            return [{
                "error": f"Failed to search notes: {str(e)}",
                "suggestion": "Ensure Full Disk Access is granted. See notes_check_availability for setup."
            }]
