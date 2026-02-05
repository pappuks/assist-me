# Assist-Me: Personal AI Assistant MCP Server

A powerful personal assistant built with security in mind. This MCP (Model Context Protocol) server provides AI access to your personal data and tools, enabling intelligent automation of daily tasks while keeping all data local.

## Overview

Assist-Me helps you automate daily tasks such as:
- ✨ Create calendar entries by analyzing emails, messages, and notes
- 📝 Generate weekly/daily to-do lists from your communications
- 🍽️ Prepare meal plans for the week
- 👨‍👩‍👧‍👦 Organize kids' study schedules and school activities
- ✈️ Plan and organize travel itineraries
- 📊 Track Amazon orders and deliveries
- 💬 Search across all your communication channels

## Tools & Integrations

| Tool | Access | Status | Platform |
|------|--------|--------|----------|
| **Gmail** | Read | ✅ Implemented | All |
| **Google Calendar** | Read/Write | ✅ Implemented | All |
| **Slack** | Read | ✅ Implemented | All |
| **iMessage** | Read | ✅ Implemented | macOS only |
| **Mac Notes** | Read | ✅ Implemented | macOS only |
| **Amazon Shopping** | Read (via email) | ✅ Implemented | All |
| **WhatsApp** | Read | ⚠️ Placeholder | See [docs](docs/whatsapp_setup.md) |

## Architecture

```
                ┌───────────────────────┐
                │     ngrok (Optional)  │
                │   Secure Web Access   │
                └───────────┬───────────┘
                            │
┌───────────────────────────┴─────────────────────────────────┐
│                        User Interface                       │
│                     (Open WebUI - Local)                    │
└───────────────────────────┬─────────────────────────────────┘
                            │
                ┌───────────┴───────────┐
                │   n8n (Optional)      │
                │  Multi-Agent Layer    │
                │  Workflow Automation  │
                └───────────┬───────────┘
                            │
┌───────────────────────────┴─────────────────────────────────┐
│                    MCP Server (This Project)                │
│                   Supports: HTTP (Streamable)               │
│  ┌──────────┬──────────┬────────┬──────────┬────────────┐   │
│  │  Gmail   │ Calendar │ Slack  │ iMessage │  Mac Notes │   │
│  └──────────┴──────────┴────────┴──────────┴────────────┘   │
└───────────────────────────┬─────────────────────────────────┘
                            │
┌───────────────────────────┴─────────────────────────────────┐
│                   Local LLM (Ollama)                        │
│             (e.g., gpt-oss-20b,gemma3, ministral-3)         │
└─────────────────────────────────────────────────────────────┘
```

**Transport Options:**
- **stdio**: Traditional standard input/output (for CLI and local desktop apps)
- **HTTP**: Streamable HTTP transport (for web applications and remote access)
- **both**: Run both transports simultaneously

**Optional Integration Layer:**
- **n8n**: An optional workflow automation platform that can sit between Open WebUI and the MCP server to build multi-agentic workflows. n8n can orchestrate complex automation tasks, combine multiple MCP tools, and expose these workflows as additional MCP servers back to Open WebUI. This enables powerful composition of AI agents and tools for advanced automation scenarios.

## Quick Start

### Prerequisites

- Python 3.10 or higher
- macOS (for iMessage and Notes features)
- 24-32 GB RAM (M-series Mac) or 16-32 GB GPU (for local LLM)

### 1. Install Dependencies

```bash
# Clone the repository
git clone https://github.com/yourusername/assist-me.git
cd assist-me

# Install Python dependencies
pip install -r requirements.txt

# For macOS-specific features, install additional packages
# Uncomment in requirements.txt:
# pyobjc-framework-Cocoa>=10.3.1
# pyobjc-framework-AppleScriptKit>=10.3.1
```

### 2. Configure Environment

```bash
# Copy example environment file
cp .env.example .env

# Edit .env with your credentials
nano .env
```

Required configuration:
```env
# Google OAuth2 (for Gmail & Calendar)
GOOGLE_CLIENT_ID=your-client-id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=your-client-secret

# Slack (optional)
SLACK_BOT_TOKEN=xoxb-your-bot-token

# Server settings
MCP_TRANSPORT=stdio  # Options: stdio, http, or both
MCP_SERVER_HOST=0.0.0.0
MCP_SERVER_PORT=8080
MCP_HTTP_JSON_RESPONSE=false  # Use SSE streams (default) or JSON responses
MCP_HTTP_STATELESS=false      # Enable stateless mode for better scaling
LOG_LEVEL=INFO
```

### 3. Setup Individual Services

Each service requires specific setup. Follow the detailed guides:

- 📧 **Gmail**: [docs/gmail_setup.md](docs/gmail_setup.md)
- 📅 **Calendar**: [docs/calendar_setup.md](docs/calendar_setup.md)
- 💬 **Slack**: [docs/slack_setup.md](docs/slack_setup.md)
- 📱 **iMessage**: [docs/imessage_setup.md](docs/imessage_setup.md)
- 📝 **Mac Notes**: [docs/notes_setup.md](docs/notes_setup.md)
- 🛒 **Amazon**: [docs/amazon_setup.md](docs/amazon_setup.md)
- ❓ **WhatsApp**: [docs/whatsapp_setup.md](docs/whatsapp_setup.md)

### 4. Run the MCP Server

The server supports three transport modes:

**Stdio Mode (Default)**:
```bash
# Run with stdio transport (for local CLI usage)
MCP_TRANSPORT=stdio python -m src.server
```

**HTTP Mode (Recommended for Web Applications)**:
```bash
# Run with HTTP transport (streamable HTTP)
MCP_TRANSPORT=http python -m src.server
```

**Both Modes**:
```bash
# Run both transports simultaneously
MCP_TRANSPORT=both python -m src.server
```

The server will:
1. Initialize all configured tools
2. Start OAuth flows for Google services (first time only)
3. Listen for MCP requests via stdio and/or HTTP (default: http://0.0.0.0:8080/mcp)

For detailed HTTP transport configuration, see [docs/http_transport.md](docs/http_transport.md)

### 5. Connect to Claude Desktop (Optional)

Claude Desktop only supports stdio-based MCP servers, so you need `mcp-remote` to bridge to your HTTP server. This requires Node.js/npx to be installed.

Add the following to your Claude Desktop configuration file at `~/Library/Application Support/Claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "assist-me": {
      "command": "npx",
      "args": [
        "mcp-remote",
        "http://localhost:8090/mcp"
      ]
    }
  }
}
```

Restart Claude Desktop to pick up the new configuration. The `mcp-remote` proxy will be downloaded automatically on first use via npx.

### 6. Install Open WebUI (Optional)

```bash
# Install Open WebUI
pip install open-webui

# Run Open WebUI
open-webui serve
```

Then configure Open WebUI to connect to the MCP server.

### 7. Install Ollama (Optional, for local LLM)

```bash
# Install Ollama
# Visit: https://ollama.com

# Pull a model
ollama pull llama2
# or
ollama pull mistral
```

### 8. Setup ngrok (Optional, for remote access)

```bash
# Install ngrok
brew install ngrok

# Setup ngrok account
# Visit: https://ngrok.com

# Run ngrok
ngrok http 8080
```

## Project Structure

```
assist-me/
├── src/
│   ├── server.py              # Main MCP server
│   ├── config/
│   │   └── settings.py        # Configuration management
│   ├── services/
│   │   └── oauth.py           # Google OAuth manager
│   └── tools/
│       ├── gmail.py           # Gmail tools
│       ├── calendar.py        # Calendar tools
│       ├── slack.py           # Slack tools
│       ├── imessage.py        # iMessage tools (macOS)
│       ├── notes.py           # Mac Notes tools (macOS)
│       ├── whatsapp.py        # WhatsApp placeholders
│       └── amazon.py          # Amazon email parsing
├── docs/                      # Detailed setup guides
├── .credentials/              # OAuth tokens (git-ignored)
├── .env                       # Environment variables (git-ignored)
├── requirements.txt           # Python dependencies
└── README.md                  # This file
```

## Available MCP Tools

### Gmail Tools
- `gmail_list_messages` - List messages with optional query
- `gmail_get_message` - Get full details of a message
- `gmail_search` - Advanced search using Gmail syntax
- `gmail_list_labels` - List all labels
- `gmail_list_accounts` - List authenticated accounts

### Calendar Tools
- `calendar_list_calendars` - List all calendars
- `calendar_list_events` - List events in date range
- `calendar_create_event` - Create new event
- `calendar_update_event` - Update existing event
- `calendar_delete_event` - Delete event
- `calendar_list_accounts` - List authenticated accounts

### Slack Tools
- `slack_list_channels` - List all channels
- `slack_read_messages` - Read messages from channel
- `slack_search_messages` - Search across workspace
- `slack_get_thread` - Get thread messages
- `slack_list_users` - List workspace users

### iMessage Tools (macOS only)
- `imessage_list_recent_conversations` - List recent chats
- `imessage_read_messages` - Read messages from contact
- `imessage_search_messages` - Search messages (placeholder)
- `imessage_check_availability` - Check system compatibility

### Mac Notes Tools (macOS only)
- `notes_list_notes` - List notes from folders
- `notes_read_note` - Read specific note
- `notes_search_notes` - Search notes by content
- `notes_list_folders` - List all folders
- `notes_check_availability` - Check system compatibility

### Amazon Tools
- `amazon_check_availability` - Check integration options
- `amazon_parse_order_emails` - Guide for parsing orders
- `amazon_search_orders` - Search orders via Gmail
- `amazon_get_deliveries` - Find upcoming deliveries

### WhatsApp Tools
- `whatsapp_check_availability` - Check integration options
- See [docs/whatsapp_setup.md](docs/whatsapp_setup.md) for details

## Security Features

### Local-First Architecture
- ✅ All data processing happens locally
- ✅ No third-party servers (except OAuth providers)
- ✅ You control your data

### Secure Authentication
- ✅ OAuth2 for Google services (Gmail, Calendar)
- ✅ API tokens for Slack
- ✅ Local-only access for iMessage and Notes
- ✅ Credentials stored in `.credentials/` (git-ignored)

### Network Security
- ✅ Optional ngrok tunnel with OAuth protection
- ✅ Configurable access restrictions
- ✅ HTTPS/TLS encryption

### Best Practices
- Never commit `.env` or `.credentials/` to version control
- Regularly rotate API tokens and credentials
- Review OAuth permissions periodically
- Use read-only scopes where possible
- Enable 2FA on all connected accounts

## System Requirements

### Minimum Requirements
- Python 3.10+
- 8 GB RAM (for MCP server only)
- Internet connection (for cloud services)

### Recommended for Full Setup
- macOS (for iMessage and Notes)
- 24-32 GB RAM (M-series Mac) or 16-32 GB GPU RAM
- 10 GB free disk space
- SSD for better performance

### Platform Compatibility

| Feature | macOS | Linux | Windows |
|---------|-------|-------|---------|
| Gmail | ✅ | ✅ | ✅ |
| Calendar | ✅ | ✅ | ✅ |
| Slack | ✅ | ✅ | ✅ |
| Amazon | ✅ | ✅ | ✅ |
| iMessage | ✅ | ❌ | ❌ |
| Mac Notes | ✅ | ❌ | ❌ |

## Usage Examples

### Create Calendar Event from Email

```python
# Search for meeting request in Gmail
emails = await gmail_search(query="meeting schedule")

# Parse email content
meeting_info = extract_meeting_details(emails[0])

# Create calendar event
await calendar_create_event(
    summary=meeting_info['title'],
    start_time=meeting_info['start'],
    end_time=meeting_info['end'],
    attendees=meeting_info['attendees']
)
```

### Track Amazon Deliveries

```python
# Find shipping notifications
deliveries = await amazon_get_deliveries(days_ahead=7)

# Add to calendar
for delivery in deliveries:
    await calendar_create_event(
        summary=f"Package Delivery: {delivery['tracking']}",
        start_time=delivery['delivery_date'],
        end_time=delivery['delivery_date']
    )
```

### Daily Digest

```python
# Get unread emails
emails = await gmail_search(query="is:unread")

# Get today's calendar
events = await calendar_list_events(
    time_min=today_start,
    time_max=today_end
)

# Get recent messages
messages = await slack_read_messages(channel_id="general", limit=20)

# Compile digest
digest = create_daily_digest(emails, events, messages)
```

## Troubleshooting

### Common Issues

**"No module named 'mcp'"**
```bash
pip install mcp
```

**"OAuth2 authentication failed"**
- Check your Google Cloud Console credentials
- Ensure redirect URI matches: `http://localhost:8080/oauth2callback`
- See [docs/gmail_setup.md](docs/gmail_setup.md)

**"iMessage tools not available"**
- Ensure you're on macOS
- Grant Terminal access in System Preferences
- See [docs/imessage_setup.md](docs/imessage_setup.md)

**"Slack authentication required"**
- Set `SLACK_BOT_TOKEN` in `.env`
- See [docs/slack_setup.md](docs/slack_setup.md)

For more issues, check the [individual setup guides](docs/).

## Development

### Running Tests

```bash
pip install -r requirements.txt
pytest
```

### Code Quality

```bash
# Format code
black src/

# Lint code
ruff check src/
```

## Acknowledgments & Credits

This project was inspired by and built upon excellent work from the MCP community:

- [mcp-google-workspace](https://github.com/j3k0/mcp-google-workspace) - Gmail and Calendar integration patterns
- [google-calendar-mcp](https://github.com/nspady/google-calendar-mcp) - Calendar implementation examples
- [google_workspace_mcp](https://github.com/taylorwilsdon/google_workspace_mcp) - Comprehensive Google Workspace integration
- [modelcontextprotocol/python-sdk](https://github.com/modelcontextprotocol/python-sdk) - Official Python MCP SDK
- [awesome-mcp-servers](https://github.com/wong2/awesome-mcp-servers) - Curated list of MCP servers

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

MIT License - see [LICENSE](LICENSE) file for details

## Privacy & Ethics

This tool accesses sensitive personal data. Please:

- Use responsibly and ethically
- Comply with all applicable laws and regulations
- Respect others' privacy in shared communications
- Be transparent about AI assistance when appropriate
- Follow terms of service for all integrated services

## Roadmap

Future enhancements:

- [ ] Telegram integration
- [ ] Discord integration
- [ ] Notion integration
- [ ] Database storage for offline access
- [ ] Web UI for configuration
- [ ] Docker containerization
- [ ] Multi-user support
- [ ] Enhanced Amazon parsing (automatic)
- [ ] WhatsApp integration (if API becomes available)
- [ ] Advanced analytics and insights

## Support

- 📖 Documentation: [docs/](docs/)
- 🐛 Issues: [GitHub Issues](https://github.com/yourusername/assist-me/issues)
- 💬 Discussions: [GitHub Discussions](https://github.com/yourusername/assist-me/discussions)

## Resources

- [Model Context Protocol Specification](https://github.com/modelcontextprotocol/modelcontextprotocol)
- [MCP Python SDK Documentation](https://modelcontextprotocol.github.io/python-sdk/)
- [Open WebUI Documentation](https://docs.openwebui.com/)
- [Ollama Documentation](https://ollama.com/docs)

---

Built with ❤️ using [Claude Code](https://claude.com/claude-code) and the Model Context Protocol. 