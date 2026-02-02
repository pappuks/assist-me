"""Configuration settings for the MCP server."""

import os
from pathlib import Path
from typing import Optional
from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Google OAuth2
    google_client_id: Optional[str] = Field(None, env="GOOGLE_CLIENT_ID")
    google_client_secret: Optional[str] = Field(None, env="GOOGLE_CLIENT_SECRET")
    google_redirect_uri: str = Field(
        "http://localhost:8080/oauth2callback", env="GOOGLE_REDIRECT_URI"
    )

    # Slack
    slack_bot_token: Optional[str] = Field(None, env="SLACK_BOT_TOKEN")
    slack_user_token: Optional[str] = Field(None, env="SLACK_USER_TOKEN")

    # Amazon
    amazon_email: Optional[str] = Field(None, env="AMAZON_EMAIL")

    # Server (HTTP Streamable transport only)
    mcp_server_port: int = Field(8090, env="MCP_SERVER_PORT")
    mcp_server_host: str = Field("0.0.0.0", env="MCP_SERVER_HOST")
    mcp_http_json_response: bool = Field(False, env="MCP_HTTP_JSON_RESPONSE")
    log_level: str = Field("INFO", env="LOG_LEVEL")

    # Directories
    credentials_dir: Path = Field(Path(".credentials"), env="CREDENTIALS_DIR")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
        extra = "ignore"  # Ignore extra env vars for backward compatibility

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Ensure credentials directory exists
        self.credentials_dir.mkdir(parents=True, exist_ok=True)


# Singleton instance
_settings: Optional[Settings] = None


def get_settings() -> Settings:
    """Get or create the settings singleton."""
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings
