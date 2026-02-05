# CLAUDE.md — Project Guide for Assist-Me MCP Server

## What is this project?

A Python MCP (Model Context Protocol) server that gives AI assistants access to personal tools: Gmail, Google Calendar, Slack, iMessage, Mac Notes, WhatsApp, and Amazon order tracking. Built with FastMCP, Starlette, and Uvicorn.

## Quick Reference

- **Language:** Python 3.10+
- **Server framework:** Starlette (ASGI) + Uvicorn
- **MCP SDK:** `mcp` package with `FastMCP` helper
- **Config:** Pydantic Settings loaded from `.env`
- **Entry point:** `src/server.py` → `main()` (Click CLI)
- **Run command:** `python -m src.server` or `assist-me-server`
- **Default endpoint:** `http://localhost:8090/mcp` (or `https://` with SSL configured)

## Project Structure

```
src/
├── server.py              # Main entry point — creates Starlette app, mounts FastMCP, runs Uvicorn
├── http_server.py          # HTTP app helper
├── config/
│   └── settings.py         # Pydantic Settings singleton (all config from .env)
├── services/
│   └── oauth.py            # Google OAuth2 manager (InstalledAppFlow, token storage)
└── tools/                  # Each file exports a register_*_tools(mcp, ...) function
    ├── __init__.py          # Re-exports all register functions
    ├── gmail.py             # Gmail read tools
    ├── calendar.py          # Google Calendar read/write tools
    ├── slack.py             # Slack read tools (currently disabled)
    ├── imessage.py          # iMessage read tools (macOS only)
    ├── notes.py             # Mac Notes read tools (macOS only)
    ├── whatsapp.py          # WhatsApp placeholder (currently disabled)
    └── amazon.py            # Amazon order tracking via Gmail (currently disabled)

docs/                       # Setup guides for each integration
prompts/                    # System prompt templates for AI assistant personas
.credentials/               # OAuth tokens (git-ignored)
.env                        # Runtime config (git-ignored)
```

## Architecture Patterns

### Tool Registration
Each tool module exports a `register_*_tools(mcp, ...)` function that registers MCP tools on the FastMCP instance. Tools are registered conditionally in `server.py:create_server()` based on:
- Available credentials (Google OAuth)
- Platform detection (`platform.system() == "Darwin"` for macOS tools)
- Environment config (Slack tokens)

### Configuration
All settings flow through `src/config/settings.py` → `Settings` (Pydantic BaseSettings). Access via `get_settings()` singleton. Key env vars:
- `MCP_SERVER_PORT` (default: 8090), `MCP_SERVER_HOST` (default: 0.0.0.0)
- `MCP_HTTP_JSON_RESPONSE` — JSON vs SSE stream responses
- `SSL_CERTFILE`, `SSL_KEYFILE` — enable HTTPS
- `GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET` — Google OAuth
- `SLACK_BOT_TOKEN`, `SLACK_USER_TOKEN` — Slack (when enabled)

### OAuth Flow
Google OAuth uses `InstalledAppFlow` with dynamic port selection (port=0) to avoid address conflicts. Credentials are stored per-account in `.credentials/` directory.

### Server Startup Flow
1. `main()` loads settings, configures logging
2. `create_server()` creates FastMCP instance, registers tools
3. Starlette app wraps FastMCP's `streamable_http_app()` at `/`
4. CORS middleware added
5. `uvicorn.run()` starts the server (with optional SSL)

## Common Tasks

### Running the server
```bash
python -m src.server                    # HTTP on port 8090
python -m src.server --port 9000        # Custom port
python -m src.server --log-level DEBUG  # Verbose logging
```

### Running with HTTPS
Set `SSL_CERTFILE` and `SSL_KEYFILE` in `.env`, then start normally. Generate certs with:
```bash
brew install mkcert && mkcert -install && mkcert localhost 127.0.0.1 ::1
```

### Code quality
```bash
black src/ --line-length 100     # Format
ruff check src/                  # Lint
pytest                           # Tests (no tests exist yet)
```

### Adding a new tool
1. Create `src/tools/new_tool.py` with a `register_new_tool_tools(mcp, ...)` function
2. Use `@mcp.tool()` decorator to register each tool function
3. Export from `src/tools/__init__.py`
4. Register conditionally in `src/server.py:create_server()`
5. Add setup docs in `docs/new_tool_setup.md`

## Currently Disabled Tools

Slack, WhatsApp, and Amazon tool registrations are commented out in `server.py` (lines ~96-123) with TODO markers. The tool implementations exist but are awaiting full integration.

## Sensitive Files (never commit)

- `.env` — contains OAuth secrets, API tokens
- `.credentials/` — contains OAuth refresh tokens
- `*.pem` — SSL certificates and keys
