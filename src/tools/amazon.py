"""Amazon Shopping tools for MCP server.

IMPORTANT: Amazon does not provide a public API for personal shopping data.

Available options:
1. Amazon Product Advertising API (for product search, not order history)
2. Web scraping Amazon.com (requires login, may violate ToS)
3. Email parsing (parse Amazon order confirmation emails from Gmail)

This module provides placeholder tools and the recommended email-parsing approach.

For production use:
- Parse Amazon order emails from Gmail (most reliable, ToS-compliant)
- Use Product Advertising API for product searches only
- Consider privacy and Terms of Service implications
"""

from typing import List, Dict, Any, Optional
from mcp.server.fastmcp import FastMCP


def register_amazon_tools(mcp: FastMCP):
    """Register Amazon Shopping-related tools with the MCP server.

    Note: These are placeholder/limited tools. Amazon does not provide an API
    for personal shopping data. See docs/amazon_setup.md for implementation options.
    """

    @mcp.tool()
    async def amazon_check_availability() -> Dict[str, Any]:
        """Check Amazon integration status and available options.

        Returns:
            Status and available implementation approaches
        """
        return {
            "status": "limited_implementation",
            "reason": "Amazon does not provide a public API for personal shopping data",
            "available_approaches": [
                {
                    "method": "Email Parsing (Recommended)",
                    "description": "Parse Amazon order confirmation emails from Gmail",
                    "requires": "Gmail integration (already available in this server)",
                    "capabilities": [
                        "Read order confirmations",
                        "Extract order details (items, prices, delivery dates)",
                        "Track shipping notifications",
                        "Find order numbers",
                    ],
                    "limitations": "Only orders with email confirmations, parsing complexity",
                    "compliance": "ToS-compliant, uses existing Gmail integration",
                },
                {
                    "method": "Amazon Product Advertising API",
                    "description": "Official API for product information and affiliate links",
                    "requires": "Amazon Associate account, API credentials",
                    "capabilities": ["Product search", "Product details", "Pricing info"],
                    "limitations": "Cannot access personal order history or account data",
                    "url": "https://webservices.amazon.com/paapi5/documentation/",
                },
                {
                    "method": "Web Scraping",
                    "description": "Scrape Amazon.com after authentication",
                    "requires": "Login credentials, browser automation (Selenium/Playwright)",
                    "limitations": "May violate Amazon ToS, fragile (breaks with UI changes)",
                    "risks": "Account suspension, legal issues, maintenance overhead",
                    "not_recommended": True,
                },
            ],
            "recommendation": (
                "Use email parsing approach: query Gmail for Amazon order emails and "
                "extract order information. This is ToS-compliant and uses the existing "
                "Gmail integration. See amazon_parse_order_emails tool."
            ),
            "documentation": "docs/amazon_setup.md",
        }

    @mcp.tool()
    async def amazon_parse_order_emails(
        max_results: int = 20,
        account_id: str = "default",
    ) -> Dict[str, Any]:
        """Parse Amazon order emails from Gmail to extract order information.

        This tool uses the Gmail integration to find and parse Amazon order emails.

        Args:
            max_results: Maximum number of order emails to parse (default: 20)
            account_id: Gmail account ID (default: "default")

        Returns:
            Instructions for using Gmail tools to parse Amazon emails

        Note:
            This is a placeholder. To implement:
            1. Use gmail_search tool with query: "from:auto-confirm@amazon.com subject:order"
            2. Parse email body to extract: order number, items, prices, delivery date
            3. Consider using a library like BeautifulSoup for HTML email parsing
        """
        return {
            "status": "implementation_guide",
            "message": (
                "Amazon order parsing requires combining Gmail tools with email parsing logic."
            ),
            "implementation_steps": [
                {
                    "step": 1,
                    "action": "Search Gmail for Amazon order emails",
                    "tool": "gmail_search",
                    "query": "from:auto-confirm@amazon.com OR from:shipment-tracking@amazon.com",
                    "example": 'Use: gmail_search(query="from:auto-confirm@amazon.com", max_results=20)',
                },
                {
                    "step": 2,
                    "action": "Get full email content",
                    "tool": "gmail_get_message",
                    "details": "For each message ID from step 1, get full email body",
                },
                {
                    "step": 3,
                    "action": "Parse email body",
                    "details": (
                        "Extract order details using regex or HTML parsing:\n"
                        "- Order number (pattern: ###-#######-#######)\n"
                        "- Item names and quantities\n"
                        "- Prices\n"
                        "- Delivery date\n"
                        "- Tracking numbers (from shipping emails)"
                    ),
                },
            ],
            "example_queries": [
                {
                    "purpose": "Find recent orders",
                    "query": "from:auto-confirm@amazon.com subject:order after:2024/01/01",
                },
                {
                    "purpose": "Find shipping updates",
                    "query": "from:shipment-tracking@amazon.com",
                },
                {
                    "purpose": "Find delivered orders",
                    "query": "from:amazon.com subject:delivered",
                },
            ],
            "future_enhancement": (
                "A future version could implement automatic email parsing. "
                "For now, use the Gmail tools directly and parse results."
            ),
            "documentation": "docs/amazon_setup.md",
        }

    @mcp.tool()
    async def amazon_search_orders(
        query: Optional[str] = None,
        days_back: int = 90,
    ) -> Dict[str, Any]:
        """Search Amazon orders using Gmail email parsing.

        Args:
            query: Optional search query (e.g., "headphones", order number)
            days_back: Number of days to search back (default: 90)

        Returns:
            Instructions for searching Amazon orders via Gmail
        """
        from datetime import datetime, timedelta

        cutoff_date = datetime.now() - timedelta(days=days_back)
        date_str = cutoff_date.strftime("%Y/%m/%d")

        gmail_query = f"from:auto-confirm@amazon.com after:{date_str}"
        if query:
            gmail_query += f" {query}"

        return {
            "status": "use_gmail_tools",
            "message": "To search Amazon orders, use the Gmail integration",
            "recommended_approach": {
                "tool": "gmail_search",
                "query": gmail_query,
                "next_step": "Parse the returned email bodies for order details",
            },
            "example": f'Use: gmail_search(query="{gmail_query}", max_results=20)',
            "parsing_tips": [
                "Look for 'Order Confirmation' in subject",
                "Extract order number from email body (format: ###-#######-#######)",
                "Parse HTML tables in email for item details",
                "Check 'Order Total' for price information",
            ],
            "documentation": "docs/amazon_setup.md",
        }

    @mcp.tool()
    async def amazon_get_deliveries(days_ahead: int = 7) -> Dict[str, Any]:
        """Get upcoming Amazon deliveries using Gmail email parsing.

        Args:
            days_ahead: Number of days ahead to check (default: 7)

        Returns:
            Instructions for finding upcoming deliveries via Gmail
        """
        return {
            "status": "use_gmail_tools",
            "message": "To find upcoming deliveries, search Amazon shipping emails in Gmail",
            "recommended_approach": {
                "tool": "gmail_search",
                "query": "from:shipment-tracking@amazon.com OR from:delivery@amazon.com",
                "next_step": "Parse email for tracking numbers and estimated delivery dates",
            },
            "parsing_tips": [
                "Look for 'arriving' or 'estimated delivery' in email body",
                "Extract tracking numbers",
                "Parse delivery date from email body",
                "Check for 'out for delivery' status",
            ],
            "alternative": (
                "You can also check your Gmail for recent Amazon emails and "
                "manually review delivery information."
            ),
            "documentation": "docs/amazon_setup.md",
        }
