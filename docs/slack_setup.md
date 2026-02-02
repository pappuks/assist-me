# Slack Setup Guide

This guide explains how to set up Slack integration for the Assist-Me MCP server.

## Prerequisites

- Slack workspace where you have admin access (or permission to install apps)
- Slack account

## Step 1: Create a Slack App

1. Go to [Slack API Apps](https://api.slack.com/apps)
2. Click **Create New App**
3. Choose **From scratch**
4. App Name: "Assist-Me Personal Assistant"
5. Select your workspace
6. Click **Create App**

## Step 2: Configure OAuth Scopes

1. In your app settings, go to **OAuth & Permissions**
2. Scroll to **Scopes** section
3. Add the following **Bot Token Scopes**:
   - `channels:history` - View messages in public channels
   - `channels:read` - View basic channel info
   - `groups:history` - View messages in private channels
   - `groups:read` - View basic private channel info
   - `im:history` - View direct messages
   - `im:read` - View basic DM info
   - `users:read` - View users in workspace
   - `search:read` - Search workspace content

4. If you need **User Token Scopes** (for searching messages you have access to):
   - `search:read`
   - `channels:history`
   - `groups:history`

## Step 3: Install App to Workspace

1. Go to **Install App** in the left sidebar
2. Click **Install to Workspace**
3. Review permissions
4. Click **Allow**
5. You'll receive a **Bot User OAuth Token** (starts with `xoxb-`)
6. If you configured user scopes, you'll also get a **User OAuth Token** (starts with `xoxp-`)

## Step 4: Configure Environment Variables

Add to your `.env` file:

```bash
# Use Bot Token for most operations
SLACK_BOT_TOKEN=xoxb-your-bot-token-here

# Optional: User Token for user-context operations
SLACK_USER_TOKEN=xoxp-your-user-token-here
```

## Step 5: Invite Bot to Channels

The bot can only read channels it has been invited to:

1. Go to the channel in Slack
2. Type `/invite @Assist-Me` (or your app name)
3. The bot can now read that channel's history

## Available Tools

- `slack_list_channels` - List all channels
- `slack_read_messages` - Read messages from a channel
- `slack_search_messages` - Search messages across workspace
- `slack_get_thread` - Get all messages in a thread
- `slack_list_users` - List users in workspace

## Usage Examples

### List Channels
```python
# List public and private channels
await slack_list_channels()

# List only public channels
await slack_list_channels(types="public_channel")
```

### Read Messages from a Channel
```python
# Recent 20 messages
await slack_read_messages(channel_id="C1234567890")

# Limit to 50 messages
await slack_read_messages(channel_id="C1234567890", limit=50)

# Messages after a specific timestamp
await slack_read_messages(
    channel_id="C1234567890",
    oldest="1609459200.000000"  # Unix timestamp
)
```

### Search Messages
```python
# Search across all channels
await slack_search_messages(query="deployment")

# More specific search
await slack_search_messages(query="from:@john deployment status")
```

### Get Thread Messages
```python
await slack_get_thread(
    channel_id="C1234567890",
    thread_ts="1609459200.000000"
)
```

### List Users
```python
await slack_list_users(limit=100)
```

## Finding Channel IDs

To find a channel ID:

1. **In Slack Desktop/Web**:
   - Right-click on the channel name
   - Select "View channel details"
   - Scroll down to find the Channel ID

2. **Using the API**:
   ```python
   channels = await slack_list_channels()
   # Find your channel in the list
   ```

## Slack Search Query Syntax

Examples of search queries:

```
deployment                           # Contains "deployment"
from:@john                          # Messages from user John
in:#general                         # Messages in #general channel
after:2024-01-01                    # Messages after date
has:link                            # Messages with links
has:attachment                      # Messages with files
is:starred                          # Starred messages
from:@john in:#engineering deployment  # Combined filters
```

## Troubleshooting

### Authentication Issues

- **"invalid_auth" error**: Check that your token is correct and starts with `xoxb-` or `xoxp-`
- **"not_authed" error**: Ensure the token is set in your `.env` file
- **Token expired**: Re-install the app to get a new token

### Permission Issues

- **"missing_scope" error**: Add the required scope in Slack App settings, then reinstall
- **"channel_not_found" error**:
  - Ensure the channel ID is correct
  - Invite the bot to the channel: `/invite @Assist-Me`
- **"not_in_channel" error**: The bot needs to be invited to private channels

### Rate Limiting

- Slack has rate limits (typically 1 request per second for most methods)
- If you hit rate limits, you'll get a `rate_limited` error
- Implement delays between requests if making many API calls

## Security Notes

- **Bot vs User Tokens**:
  - Bot tokens (`xoxb-`) are safer and recommended for most use cases
  - User tokens (`xoxp-`) act as you and have access to your DMs and private content
- Keep tokens secure and never commit to version control
- Regularly rotate tokens in production
- Use the minimum required scopes
- Review app permissions in Slack workspace settings

## Privacy Considerations

- The bot can read all messages in channels it's invited to
- Be transparent with team members about the bot's capabilities
- Consider data retention policies for any stored messages
- Comply with your organization's security and privacy policies

## References

- [Slack API Documentation](https://api.slack.com/docs)
- [Slack Python SDK](https://slack.dev/python-slack-sdk/)
- [OAuth Scopes Reference](https://api.slack.com/scopes)
- [Slack MCP Servers List](https://github.com/wong2/awesome-mcp-servers)
