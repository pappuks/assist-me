"""HTTP server implementation for MCP Streamable HTTP transport.

This module provides utilities for creating HTTP servers using Starlette and MCP.
The main implementation is in server.py which uses FastMCP.

Note: This module is kept for backward compatibility. The recommended approach
is to use FastMCP directly as shown in server.py.
"""

import contextlib
import logging

from starlette.applications import Starlette
from starlette.routing import Mount
from mcp.server.fastmcp import FastMCP

logger = logging.getLogger(__name__)


def create_http_app(
    mcp_server: FastMCP,
    mount_path: str = "/mcp",
) -> Starlette:
    """Create and configure the Starlette application with MCP StreamableHTTP.

    This function uses FastMCP's streamable_http_app() method to create
    a simplified HTTP server following the MCP specification pattern.

    Args:
        mcp_server: The FastMCP server instance with registered tools
        mount_path: Path to mount the MCP server (default: "/mcp")

    Returns:
        Configured Starlette application

    Example:
        >>> from mcp.server.fastmcp import FastMCP
        >>> mcp = FastMCP("my-app", json_response=True)
        >>> app = create_http_app(mcp)
    """

    # Create a lifespan context manager to run the session manager
    @contextlib.asynccontextmanager
    async def lifespan(app: Starlette):
        async with mcp_server.session_manager.run():
            logger.info("Application started with StreamableHTTP session manager")
            try:
                yield
            finally:
                logger.info("Application shutting down...")

    # Mount the StreamableHTTP server to the ASGI server
    starlette_app = Starlette(
        routes=[Mount(mount_path, app=mcp_server.streamable_http_app())],
        lifespan=lifespan,
    )

    return starlette_app
