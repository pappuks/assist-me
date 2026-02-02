"""OAuth2 authentication management for Google services.

Inspired by: https://github.com/j3k0/mcp-google-workspace
"""

import json
import os
from pathlib import Path
from typing import Optional, List, Dict, Any
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# Google API Scopes
GMAIL_SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]
CALENDAR_SCOPES = ["https://www.googleapis.com/auth/calendar"]


class GoogleOAuthManager:
    """Manages OAuth2 authentication for Google services."""

    def __init__(
        self,
        client_id: str,
        client_secret: str,
        redirect_uri: str,
        credentials_dir: Path,
    ):
        """Initialize the OAuth manager.

        Args:
            client_id: Google OAuth2 client ID
            client_secret: Google OAuth2 client secret
            redirect_uri: OAuth2 redirect URI
            credentials_dir: Directory to store credentials
        """
        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_uri = redirect_uri
        self.credentials_dir = Path(credentials_dir)
        self.credentials_dir.mkdir(parents=True, exist_ok=True)

    def _get_credentials_path(self, account_id: str, service: str) -> Path:
        """Get the path to the credentials file for a specific account and service."""
        return self.credentials_dir / f"{account_id}_{service}_token.json"

    def get_credentials(
        self, account_id: str, service: str, scopes: List[str]
    ) -> Optional[Credentials]:
        """Get or refresh credentials for a specific account and service.

        Args:
            account_id: Unique identifier for the account
            service: Service name (e.g., 'gmail', 'calendar')
            scopes: Required OAuth2 scopes

        Returns:
            Valid credentials or None if authentication is needed
        """
        creds_path = self._get_credentials_path(account_id, service)
        creds = None

        # Load existing credentials
        if creds_path.exists():
            creds = Credentials.from_authorized_user_file(str(creds_path), scopes)

        # Refresh or get new credentials
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                # Create client config
                client_config = {
                    "installed": {
                        "client_id": self.client_id,
                        "client_secret": self.client_secret,
                        "redirect_uris": [self.redirect_uri],
                        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                        "token_uri": "https://oauth2.googleapis.com/token",
                    }
                }

                flow = InstalledAppFlow.from_client_config(client_config, scopes)
                # Use port 0 to let OS choose an available port dynamically
                # This prevents "Address already in use" errors
                creds = flow.run_local_server(
                    port=0,
                    open_browser=True,
                    success_message="Authentication successful! You can close this window."
                )

            # Save the credentials
            with open(creds_path, "w") as token:
                token.write(creds.to_json())

        return creds

    def build_gmail_service(self, account_id: str = "default"):
        """Build a Gmail API service.

        Args:
            account_id: Account identifier

        Returns:
            Gmail API service object
        """
        creds = self.get_credentials(account_id, "gmail", GMAIL_SCOPES)
        if not creds:
            raise ValueError(f"No valid credentials for Gmail account: {account_id}")
        return build("gmail", "v1", credentials=creds)

    def build_calendar_service(self, account_id: str = "default"):
        """Build a Google Calendar API service.

        Args:
            account_id: Account identifier

        Returns:
            Calendar API service object
        """
        creds = self.get_credentials(account_id, "calendar", CALENDAR_SCOPES)
        if not creds:
            raise ValueError(f"No valid credentials for Calendar account: {account_id}")
        return build("calendar", "v3", credentials=creds)

    def list_authenticated_accounts(self, service: str) -> List[str]:
        """List all authenticated accounts for a service.

        Args:
            service: Service name (e.g., 'gmail', 'calendar')

        Returns:
            List of account IDs
        """
        pattern = f"*_{service}_token.json"
        accounts = []
        for creds_file in self.credentials_dir.glob(pattern):
            account_id = creds_file.stem.replace(f"_{service}_token", "")
            accounts.append(account_id)
        return accounts
