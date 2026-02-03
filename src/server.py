"""Main MCP Server for Assist-Me Personal Assistant.

This server provides tools for integrating with:
- Gmail (read access)
- Google Calendar (read/write)
- Slack (read)
- iMessage (read, macOS only)
- Mac Notes (read, macOS only)
- WhatsApp (placeholder - see docs)
- Amazon Shopping (email parsing via Gmail)

Inspired by:
- https://github.com/j3k0/mcp-google-workspace
- https://github.com/taylorwilsdon/google_workspace_mcp
- https://github.com/modelcontextprotocol/python-sdk
"""

import contextlib
import logging

import click
import uvicorn
from mcp.server.fastmcp import FastMCP
from starlette.applications import Starlette
from starlette.middleware.cors import CORSMiddleware
from starlette.routing import Mount

from .config import get_settings
from .services.oauth import GoogleOAuthManager
from .tools import (
    register_gmail_tools,
    register_calendar_tools,
    register_slack_tools,
    register_imessage_tools,
    register_notes_tools,
    register_whatsapp_tools,
    register_amazon_tools,
)

# Configure logging
logger = logging.getLogger(__name__)


def initialize_oauth_manager(settings) -> GoogleOAuthManager | None:
    """Initialize OAuth manager for Google services.

    Args:
        settings: Application settings

    Returns:
        GoogleOAuthManager instance or None if credentials not configured
    """
    if settings.google_client_id and settings.google_client_secret:
        oauth_manager = GoogleOAuthManager(
            client_id=settings.google_client_id,
            client_secret=settings.google_client_secret,
            redirect_uri=settings.google_redirect_uri,
            credentials_dir=settings.credentials_dir,
        )
        logger.info("Google OAuth manager initialized")
        return oauth_manager
    else:
        logger.warning(
            "Google OAuth credentials not configured. "
            "Gmail and Calendar tools will not be available."
        )
        return None


def create_server(json_response: bool = False) -> FastMCP:
    """Create and configure the MCP server.

    Args:
        json_response: If True, return JSON responses instead of SSE streams

    Returns:
        Configured FastMCP server instance
    """
    mcp = FastMCP("assist-me", json_response=json_response)
    settings = get_settings()

    # Register tools based on available configuration
    logger.info("Registering tools...")

    # Initialize OAuth manager for Google services
    oauth_manager = initialize_oauth_manager(settings)

    # Google Workspace tools (Gmail, Calendar)
    if oauth_manager:
        register_gmail_tools(mcp, oauth_manager)
        register_calendar_tools(mcp, oauth_manager)
        logger.info("Registered Gmail and Calendar tools")
    else:
        logger.warning("Skipping Gmail and Calendar tools (no OAuth credentials)")

    # TODO: Enable Slack tools when implemented
    # # Slack tools
    # slack_token = settings.slack_bot_token or settings.slack_user_token
    # register_slack_tools(mcp, slack_token)
    # if slack_token:
    #     logger.info("Registered Slack tools")
    # else:
    #     logger.warning("Slack tools registered but require authentication")

    # macOS-specific tools
    import platform

    if platform.system() == "Darwin":
        register_imessage_tools(mcp)
        register_notes_tools(mcp)
        logger.info("Registered iMessage and Notes tools (macOS)")
    else:
        logger.info("Skipping iMessage and Notes tools (not on macOS)")

    # TODO: Enable WhatsApp tools when implemented
    # # WhatsApp (placeholder)
    # register_whatsapp_tools(mcp)
    # logger.info("Registered WhatsApp placeholder tools")

    # TODO: Enable Amazon tools when implemented
    # # Amazon (email parsing via Gmail)
    # register_amazon_tools(mcp)
    # logger.info("Registered Amazon tools (email parsing)")

    logger.info("All tools registered successfully")
    return mcp


@click.command()
@click.option("--port", default=None, help="Port to listen on for HTTP (overrides MCP_SERVER_PORT env var)")
@click.option(
    "--log-level",
    default=None,
    help="Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL) (overrides LOG_LEVEL env var)",
)
@click.option(
    "--json-response",
    is_flag=True,
    default=None,
    help="Enable JSON responses instead of SSE streams (overrides MCP_HTTP_JSON_RESPONSE env var)",
)
def main(
    port: int | None,
    log_level: str | None,
    json_response: bool | None,
) -> int:
    """Run the Assist-Me MCP Server using HTTP Streamable transport."""
    # Load settings from environment
    settings = get_settings()

    # Override settings with CLI arguments if provided
    if port is not None:
        settings.mcp_server_port = port
    if log_level is not None:
        settings.log_level = log_level.upper()
    if json_response is not None:
        settings.mcp_http_json_response = json_response

    # Configure logging
    logging.basicConfig(
        level=getattr(logging, settings.log_level.upper()),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    logger.info("Starting Assist-Me MCP Server...")
    logger.info(f"Host: {settings.mcp_server_host}")
    logger.info(f"Port: {settings.mcp_server_port}")
    logger.info(f"Log level: {settings.log_level}")
    logger.info(f"JSON response mode: {settings.mcp_http_json_response}")

    # Create the MCP server
    mcp = create_server(json_response=settings.mcp_http_json_response)

    # Create a lifespan context manager to run the session manager
    @contextlib.asynccontextmanager
    async def lifespan(app: Starlette):
        async with mcp.session_manager.run():
            logger.info("Application started with StreamableHTTP session manager")
            try:
                yield
            finally:
                logger.info("Application shutting down...")

    # Create Starlette app with FastMCP's streamable HTTP app
    # Mount at root - FastMCP handles the /mcp endpoint internally
    starlette_app = Starlette(
        routes=[Mount("/", app=mcp.streamable_http_app())],
        lifespan=lifespan,
    )

    # Wrap with CORS middleware to handle OPTIONS requests
    starlette_app = CORSMiddleware(
        starlette_app,
        allow_origins=["*"],  # Allow all origins - adjust for production
        allow_methods=["GET", "POST", "DELETE", "OPTIONS"],  # Include OPTIONS for CORS
        allow_headers=["*"],
        expose_headers=["Mcp-Session-Id"],
    )

    # Run the server
    logger.info(
        f"MCP server listening at http://{settings.mcp_server_host}:{settings.mcp_server_port}/mcp"
    )
    uvicorn.run(
        starlette_app,
        host=settings.mcp_server_host,
        port=settings.mcp_server_port,
        log_level=settings.log_level.lower(),
    )

    return 0


def run():
    """Run the server (synchronous entry point)."""
    main()


if __name__ == "__main__":
    run()
