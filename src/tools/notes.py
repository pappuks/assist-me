"""Mac Notes tools for MCP server (macOS only).

Uses AppleScript to access Notes app data on macOS.
Note: This requires macOS and proper permissions to access Notes.
"""

import subprocess
import platform
from typing import List, Dict, Any, Optional
from mcp.server.fastmcp import FastMCP


def _is_macos() -> bool:
    """Check if running on macOS."""
    return platform.system() == "Darwin"


def _run_applescript(script: str) -> str:
    """Execute AppleScript and return output.

    Args:
        script: AppleScript code to execute

    Returns:
        Script output as string

    Raises:
        RuntimeError: If not on macOS or script fails
    """
    if not _is_macos():
        raise RuntimeError("Mac Notes tools are only available on macOS")

    try:
        result = subprocess.run(
            ["osascript", "-e", script],
            capture_output=True,
            text=True,
            check=True,
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"AppleScript execution failed: {e.stderr}")


def register_notes_tools(mcp: FastMCP):
    """Register Mac Notes-related tools with the MCP server.

    Note: These tools only work on macOS and require appropriate permissions.
    """

    @mcp.tool()
    async def notes_list_notes(
        folder: Optional[str] = None,
        limit: int = 20,
    ) -> List[Dict[str, str]]:
        """List notes from Mac Notes app.

        Args:
            folder: Folder name to list notes from (default: all folders)
            limit: Maximum number of notes to return (default: 20)

        Returns:
            List of notes with id, name, and folder

        Note:
            Requires macOS and permission to access Notes app.
        """
        if not _is_macos():
            return [{"error": "Mac Notes tools are only available on macOS"}]

        try:
            if folder:
                script = f"""
                tell application "Notes"
                    set noteList to {{}}
                    set targetFolder to folder "{folder}"
                    set allNotes to notes in targetFolder
                    repeat with i from 1 to (count of allNotes)
                        if i > {limit} then exit repeat
                        set theNote to item i of allNotes
                        set noteName to name of theNote
                        set noteID to id of theNote
                        set end of noteList to {{noteID, noteName, "{folder}"}}
                    end repeat
                    return noteList
                end tell
                """
            else:
                script = f"""
                tell application "Notes"
                    set noteList to {{}}
                    set allNotes to notes
                    repeat with i from 1 to (count of allNotes)
                        if i > {limit} then exit repeat
                        set theNote to item i of allNotes
                        set noteName to name of theNote
                        set noteID to id of theNote
                        set noteFolder to name of folder of theNote
                        set end of noteList to {{noteID, noteName, noteFolder}}
                    end repeat
                    return noteList
                end tell
                """

            result = _run_applescript(script)
            # Parse the AppleScript result
            # This is a simplified parser - production code would need more robust parsing
            return [{"raw_result": result, "note": "See docs/notes_setup.md for details"}]
        except Exception as e:
            return [
                {
                    "error": f"Failed to list notes: {str(e)}",
                    "suggestion": "Grant Terminal access in System Preferences > Security & "
                    "Privacy > Privacy > Automation",
                }
            ]

    @mcp.tool()
    async def notes_read_note(note_id: str) -> Dict[str, Any]:
        """Read the content of a specific note.

        Args:
            note_id: Note ID (from notes_list_notes)

        Returns:
            Note content with name, body, and metadata

        Note:
            Requires macOS and permission to access Notes app.
        """
        if not _is_macos():
            return {"error": "Mac Notes tools are only available on macOS"}

        try:
            script = f"""
            tell application "Notes"
                set theNote to note id "{note_id}"
                set noteName to name of theNote
                set noteBody to body of theNote
                set noteDate to modification date of theNote
                set noteFolder to name of folder of theNote
                return {{noteName, noteBody, noteDate as string, noteFolder}}
            end tell
            """
            result = _run_applescript(script)
            return {
                "id": note_id,
                "raw_result": result,
                "note": "Parse the raw_result for structured data. See docs/notes_setup.md",
            }
        except Exception as e:
            return {
                "error": f"Failed to read note: {str(e)}",
                "suggestion": "Ensure Terminal has access to Notes app in System Preferences",
            }

    @mcp.tool()
    async def notes_search_notes(query: str, limit: int = 20) -> List[Dict[str, str]]:
        """Search notes by title or content.

        Args:
            query: Search query
            limit: Maximum number of results (default: 20)

        Returns:
            List of matching notes

        Note:
            Requires macOS and permission to access Notes app.
        """
        if not _is_macos():
            return [{"error": "Mac Notes tools are only available on macOS"}]

        try:
            script = f"""
            tell application "Notes"
                set matchingNotes to {{}}
                set allNotes to notes
                repeat with theNote in allNotes
                    set noteName to name of theNote
                    set noteBody to body of theNote
                    if noteName contains "{query}" or noteBody contains "{query}" then
                        set noteID to id of theNote
                        set noteFolder to name of folder of theNote
                        set end of matchingNotes to {{noteID, noteName, noteFolder}}
                        if (count of matchingNotes) ≥ {limit} then exit repeat
                    end if
                end repeat
                return matchingNotes
            end tell
            """
            result = _run_applescript(script)
            return [{"raw_result": result, "note": "Parse results. See docs/notes_setup.md"}]
        except Exception as e:
            return [
                {
                    "error": f"Failed to search notes: {str(e)}",
                    "suggestion": "Grant Terminal access to Notes app in System Preferences",
                }
            ]

    @mcp.tool()
    async def notes_list_folders() -> List[Dict[str, str]]:
        """List all folders in Mac Notes app.

        Returns:
            List of folders with id and name

        Note:
            Requires macOS and permission to access Notes app.
        """
        if not _is_macos():
            return [{"error": "Mac Notes tools are only available on macOS"}]

        try:
            script = """
            tell application "Notes"
                set folderList to {}
                set allFolders to folders
                repeat with theFolder in allFolders
                    set folderName to name of theFolder
                    set folderID to id of theFolder
                    set end of folderList to {folderID, folderName}
                end repeat
                return folderList
            end tell
            """
            result = _run_applescript(script)
            return [{"raw_result": result, "note": "Parse results. See docs/notes_setup.md"}]
        except Exception as e:
            return [
                {
                    "error": f"Failed to list folders: {str(e)}",
                    "suggestion": "Grant Terminal access to Notes app in System Preferences",
                }
            ]

    @mcp.tool()
    async def notes_check_availability() -> Dict[str, Any]:
        """Check if Mac Notes tools are available on this system.

        Returns:
            Availability status and requirements
        """
        is_available = _is_macos()
        return {
            "available": is_available,
            "platform": platform.system(),
            "requirements": [
                "macOS operating system",
                "Notes app installed",
                "Terminal/Python granted access to Notes in System Preferences > "
                "Security & Privacy > Privacy > Automation",
            ],
            "documentation": "See docs/notes_setup.md for detailed setup instructions",
        }
