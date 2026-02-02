# Gmail Setup Guide

This guide explains how to set up Gmail integration for the Assist-Me MCP server.

## Prerequisites

- Google account with Gmail
- Access to Google Cloud Console

## Step 1: Create Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Note your project ID

## Step 2: Enable Gmail API

1. In the Google Cloud Console, go to **APIs & Services > Library**
2. Search for "Gmail API"
3. Click on "Gmail API" and click **Enable**

## Step 3: Create OAuth 2.0 Credentials

1. Go to **APIs & Services > Credentials**
2. Click **Create Credentials** > **OAuth client ID**
3. If prompted, configure the OAuth consent screen:
   - Select **External** user type (or Internal if using Google Workspace)
   - Fill in the app name (e.g., "Assist-Me Personal Assistant")
   - Add your email as a developer contact
   - Add scopes: `https://www.googleapis.com/auth/gmail.readonly`
   - Add test users (your own email) if using External type
4. Create OAuth client ID:
   - Application type: **Desktop app**
   - Name: "Assist-Me Desktop Client"
   - Click **Create**
5. Download the credentials JSON or copy the Client ID and Client Secret

## Step 4: Configure Environment Variables

Create a `.env` file in the project root (copy from `.env.example`):

```bash
GOOGLE_CLIENT_ID=your-client-id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=your-client-secret
GOOGLE_REDIRECT_URI=http://localhost:8080/oauth2callback
```

## Step 5: Authenticate

1. Run the MCP server for the first time
2. When you use a Gmail tool, a browser window will open for OAuth authentication
3. Sign in with your Google account
4. Grant the requested permissions
5. The credentials will be saved in `.credentials/default_gmail_token.json`

## Multiple Accounts

To use multiple Gmail accounts:

1. When calling Gmail tools, specify different `account_id` values
2. Each account will trigger its own OAuth flow
3. Credentials are stored separately: `.credentials/{account_id}_gmail_token.json`

Example:
```python
# Use work account
await gmail_list_messages(account_id="work", query="is:unread")

# Use personal account
await gmail_list_messages(account_id="personal", query="is:unread")
```

## Available Tools

- `gmail_list_messages` - List messages with optional query
- `gmail_get_message` - Get full details of a specific message
- `gmail_search` - Search messages using Gmail query syntax
- `gmail_list_labels` - List all Gmail labels
- `gmail_list_accounts` - List authenticated accounts

## Gmail Search Syntax Examples

```
is:unread                              # Unread messages
from:example@gmail.com                 # From specific sender
subject:meeting                        # Subject contains "meeting"
has:attachment                         # Has attachments
larger:5M                              # Larger than 5MB
after:2024/01/01                       # After specific date
from:john subject:report after:2024/01/01  # Combined filters
```

## Troubleshooting

### Authentication Issues

- **"Error 400: redirect_uri_mismatch"**: Ensure the redirect URI in your `.env` matches exactly what's configured in Google Cloud Console
- **"Access blocked: This app's request is invalid"**: Make sure you've configured the OAuth consent screen and added test users
- **Token expired**: Delete the token file in `.credentials/` and re-authenticate

### Permission Issues

- Ensure Gmail API is enabled in Google Cloud Console
- Check that the OAuth consent screen includes the correct scopes
- Add your email as a test user if using External user type

## Security Notes

- Keep your `.env` file secure and never commit it to version control
- The `.credentials` directory contains sensitive tokens - add it to `.gitignore`
- For production use, consider using Google Workspace with internal user type
- Regularly review and rotate credentials

## References

- Inspired by [mcp-google-workspace](https://github.com/j3k0/mcp-google-workspace)
- [Gmail API Documentation](https://developers.google.com/gmail/api)
- [Google OAuth 2.0 Guide](https://developers.google.com/identity/protocols/oauth2)
