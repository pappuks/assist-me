# Amazon Shopping Setup Guide

⚠️ **Important**: Amazon does not provide a public API for personal shopping data (orders, account info).

This guide explains the available options and recommended approach for accessing your Amazon data.

## Current Status

The Assist-Me MCP server includes **email parsing tools** for Amazon, leveraging the existing Gmail integration to extract order information from Amazon emails.

## Why No Direct Integration?

1. **No Public API**: Amazon doesn't provide an API for personal order history
2. **Scraping Risks**: Web scraping may violate Amazon ToS
3. **Authentication Complexity**: Maintaining login sessions is unreliable
4. **Fragility**: UI changes break scraping implementations

## Available Options

### Option 1: Email Parsing (Recommended & Implemented)

**Approach**: Parse Amazon order confirmation and shipping emails from Gmail

**Advantages**:
- ✅ Uses existing Gmail integration
- ✅ ToS-compliant
- ✅ No additional authentication needed
- ✅ Reliable and stable
- ✅ Works with past orders

**How It Works**:
1. Query Gmail for Amazon emails
2. Parse order confirmations for:
   - Order numbers
   - Item details
   - Prices
   - Delivery dates
   - Tracking numbers

**Setup**: No additional setup needed! Just configure Gmail (see [gmail_setup.md](gmail_setup.md))

### Option 2: Amazon Product Advertising API (Product Search Only)

**Best for**: Product search, price checking (not order history)

**Capabilities**:
- Search products
- Get product details
- Check current prices
- Generate affiliate links

**Limitations**:
- ❌ Cannot access personal orders
- ❌ Cannot access account data
- ❌ Requires Amazon Associate account

**Setup**:
1. Sign up for [Amazon Associates](https://affiliate-program.amazon.com/)
2. Get approved
3. Apply for Product Advertising API access
4. Get API credentials

**Not Implemented** because it doesn't provide personal shopping data.

**Resources**:
- [PA API 5.0 Documentation](https://webservices.amazon.com/paapi5/documentation/)

### Option 3: Web Scraping (Not Recommended)

**Warning**: May violate Amazon Terms of Service.

**Approach**: Automate web browser to scrape order pages

**Risks**:
- ⚠️ May violate ToS
- ⚠️ Account suspension risk
- ⚠️ Breaks with UI changes
- ⚠️ Login captchas
- ⚠️ IP blocking

**Not Implemented** due to risks and reliability issues.

## Implemented Tools

The Assist-Me server provides these Amazon tools:

### amazon_check_availability

Get information about Amazon integration options and current implementation.

```python
info = await amazon_check_availability()
# Returns details about email parsing approach
```

### amazon_parse_order_emails

Get implementation guide for parsing Amazon order emails.

```python
guide = await amazon_parse_order_emails(max_results=20)
# Returns step-by-step guide for using Gmail tools
```

### amazon_search_orders

Search for Amazon orders using Gmail queries.

```python
results = await amazon_search_orders(query="headphones", days_back=90)
# Returns Gmail query to find relevant order emails
```

### amazon_get_deliveries

Find upcoming Amazon deliveries from shipping emails.

```python
deliveries = await amazon_get_deliveries(days_ahead=7)
# Returns Gmail query for tracking emails
```

## Using Email Parsing

### Step 1: Search for Order Emails

Use the Gmail integration to find Amazon emails:

```python
# Recent orders
orders = await gmail_search(
    query="from:auto-confirm@amazon.com subject:order after:2024/01/01",
    max_results=20
)
```

### Step 2: Get Email Content

Retrieve full email details:

```python
for order in orders:
    email_detail = await gmail_get_message(message_id=order['id'])
    # email_detail contains the email body
```

### Step 3: Parse Order Information

Extract order details from email body:

```python
import re

def parse_amazon_order_email(email_body):
    """Extract order info from Amazon confirmation email."""

    # Order number (format: ###-#######-#######)
    order_match = re.search(r'Order #(\d{3}-\d{7}-\d{7})', email_body)
    order_number = order_match.group(1) if order_match else None

    # Order total
    total_match = re.search(r'Order Total: \$([0-9,.]+)', email_body)
    total = total_match.group(1) if total_match else None

    # Delivery date
    delivery_match = re.search(
        r'Delivery estimate[:\s]+([A-Za-z]+\s+\d{1,2},\s+\d{4})',
        email_body
    )
    delivery_date = delivery_match.group(1) if delivery_match else None

    return {
        'order_number': order_number,
        'total': total,
        'delivery_date': delivery_date
    }
```

### Complete Example

```python
async def get_recent_amazon_orders(days=30):
    """Get recent Amazon orders from Gmail."""
    from datetime import datetime, timedelta

    # Calculate date threshold
    cutoff = datetime.now() - timedelta(days=days)
    date_str = cutoff.strftime('%Y/%m/%d')

    # Search Gmail
    orders = await gmail_search(
        query=f"from:auto-confirm@amazon.com after:{date_str}",
        max_results=50
    )

    # Parse each order
    parsed_orders = []
    for order in orders:
        email = await gmail_get_message(message_id=order['id'])
        parsed = parse_amazon_order_email(email['body'])
        parsed['date'] = email['date']
        parsed['subject'] = email['subject']
        parsed_orders.append(parsed)

    return parsed_orders
```

## Gmail Query Examples for Amazon

### Order Confirmations
```
from:auto-confirm@amazon.com subject:order
from:auto-confirm@amazon.com after:2024/01/01
from:auto-confirm@amazon.com "Order Confirmation"
```

### Shipping Notifications
```
from:shipment-tracking@amazon.com
from:delivery@amazon.com
from:amazon.com subject:"out for delivery"
from:amazon.com subject:delivered
```

### Returns and Refunds
```
from:amazon.com subject:refund
from:amazon.com subject:"return"
subject:"Amazon.com order" refund
```

### Subscribe & Save
```
from:amazon.com subject:"Subscribe & Save"
from:auto-confirm@amazon.com "Subscribe & Save"
```

### Digital Orders
```
from:digital-no-reply@amazon.com
from:amazon.com subject:"Thank you for your order"
subject:"Amazon.com order" kindle
```

## Parsing Different Email Types

### Order Confirmation Email

Key information to extract:
- Order number
- Order total
- Items ordered
- Delivery estimate
- Shipping address

### Shipping Notification Email

Key information:
- Tracking number
- Carrier
- Estimated delivery date
- Package details

### Delivery Confirmation Email

Key information:
- Delivered date/time
- Delivery location
- Package recipient

## Advanced Parsing with HTML

Amazon emails are HTML-formatted. Use BeautifulSoup for better parsing:

```python
from bs4 import BeautifulSoup

def parse_amazon_html_email(html_content):
    """Parse Amazon HTML email for structured data."""
    soup = BeautifulSoup(html_content, 'html.parser')

    # Find order number
    order_num_tag = soup.find(string=re.compile(r'Order #\d{3}-\d{7}-\d{7}'))

    # Find order items table
    items_table = soup.find('table', class_='order-items')

    # Extract item details
    items = []
    if items_table:
        for row in items_table.find_all('tr'):
            cells = row.find_all('td')
            if len(cells) >= 2:
                items.append({
                    'name': cells[0].get_text(strip=True),
                    'price': cells[1].get_text(strip=True)
                })

    return {
        'order_number': extract_order_number(order_num_tag),
        'items': items
    }
```

## Tracking Deliveries

To get upcoming deliveries:

```python
async def get_upcoming_deliveries():
    """Find packages arriving soon."""

    # Search for recent shipping emails
    emails = await gmail_search(
        query="from:shipment-tracking@amazon.com OR from:delivery@amazon.com",
        max_results=20
    )

    deliveries = []
    for email in emails:
        detail = await gmail_get_message(message_id=email['id'])

        # Look for delivery date in email
        delivery_match = re.search(
            r'arriving ([A-Za-z]+day, [A-Za-z]+ \d{1,2})',
            detail['body']
        )

        # Extract tracking number
        tracking_match = re.search(
            r'Tracking ID:?\s*([A-Z0-9]+)',
            detail['body']
        )

        if delivery_match or tracking_match:
            deliveries.append({
                'delivery_date': delivery_match.group(1) if delivery_match else None,
                'tracking': tracking_match.group(1) if tracking_match else None,
                'email_date': detail['date']
            })

    return deliveries
```

## Installation Requirements

For HTML parsing, install BeautifulSoup:

```bash
pip install beautifulsoup4 lxml
```

Already included in project dependencies.

## Limitations

### Email Parsing Limitations

1. **Email Delivery**: Requires order confirmation emails
2. **Parsing Complexity**: Email formats may change
3. **Incomplete Data**: Not all details in emails
4. **Historical Data**: Limited to emails you've received

### What You Can't Get

- Order history before you started saving emails
- Account balance/gift cards
- Wish list items
- Browsing history
- Prime video watch history
- Kindle library details

## Alternative: Manual Export

For comprehensive order history:

1. **Download Order History**:
   - Go to Amazon.com
   - Account & Lists > Orders
   - Filter to desired date range
   - Click "Export to CSV" (if available)

2. **Process CSV**:
   ```python
   import csv

   def parse_amazon_csv(file_path):
       orders = []
       with open(file_path, 'r') as f:
           reader = csv.DictReader(f)
           for row in reader:
               orders.append({
                   'order_date': row['Order Date'],
                   'order_id': row['Order ID'],
                   'title': row['Title'],
                   'amount': row['Item Total']
               })
       return orders
   ```

## Future Enhancements

Potential improvements:

1. **Automatic Parsing**: Pre-built parsers for common email formats
2. **Database Storage**: Store parsed orders locally
3. **Price Tracking**: Track price changes from emails
4. **Delivery Calendar**: Export to Google Calendar
5. **Spending Analysis**: Monthly/yearly reports

## Security & Privacy

### Email Access
- Emails may contain sensitive information
- Order details, addresses, payment info
- Keep parsed data secure

### Best Practices
1. Don't store payment card numbers
2. Encrypt stored order data
3. Regular cleanup of old data
4. Respect privacy in shared environments

## Troubleshooting

### No Emails Found
- Check Gmail authentication
- Verify email forwarding settings
- Check spam folder
- Adjust date range

### Parsing Errors
- Email format may have changed
- Test with recent emails first
- Check HTML vs plain text
- Update regex patterns

### Missing Information
- Not all details in emails
- Digital orders may have different format
- Subscribe & Save orders vary
- International orders may differ

## References

- [Gmail Setup Guide](gmail_setup.md)
- Amazon order email examples (in your own inbox)
- [BeautifulSoup Documentation](https://www.crummy.com/software/BeautifulSoup/bs4/doc/)
- [Python Regex Guide](https://docs.python.org/3/howto/regex.html)

## Recommended Workflow

1. **Setup Gmail Integration**: Follow [gmail_setup.md](gmail_setup.md)
2. **Test Email Search**: Verify you can find Amazon emails
3. **Sample Parsing**: Parse a few recent orders manually
4. **Build Parser**: Create regex/parsing logic for your email format
5. **Automate**: Integrate into your workflows
6. **Monitor**: Update parsers when Amazon changes email format

This approach provides reliable, ToS-compliant access to your Amazon order data through email parsing.
