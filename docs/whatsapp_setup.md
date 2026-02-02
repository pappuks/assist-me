# WhatsApp Setup Guide

⚠️ **Important**: WhatsApp does not provide an official API for personal accounts.

This guide explains the available options and limitations for WhatsApp integration.

## Current Status

The Assist-Me MCP server includes **placeholder tools** for WhatsApp. These tools return information about implementation options but do not provide actual WhatsApp integration.

## Why No Direct Integration?

1. **No Official API**: WhatsApp doesn't provide a public API for personal accounts
2. **Terms of Service**: Unofficial methods may violate WhatsApp ToS
3. **Account Risk**: Using unofficial methods can result in account bans
4. **Security Concerns**: Third-party access to messaging requires careful consideration

## Available Options

### Option 1: WhatsApp Business API (Business Accounts Only)

**Best for**: Business use cases, official customer communication

**Setup**:
1. Create a WhatsApp Business account
2. Apply for Business API access through Meta
3. Get approved (requires business verification)
4. Use official API

**Capabilities**:
- Send template messages
- Receive customer messages
- Automated responses
- Integration with CRM systems

**Limitations**:
- Cannot access personal WhatsApp messages
- Requires business verification
- Monthly costs may apply
- Limited to business communications

**Resources**:
- [WhatsApp Business API Docs](https://developers.facebook.com/docs/whatsapp)
- [Getting Started Guide](https://developers.facebook.com/docs/whatsapp/getting-started)

### Option 2: Web Automation (Unofficial, Not Recommended)

**Warning**: May violate WhatsApp Terms of Service and risk account suspension.

**Approach**: Automate WhatsApp Web using browser automation

**Technologies**:
- **Node.js**: whatsapp-web.js
- **Python**: selenium, playwright

**Example (whatsapp-web.js)**:
```javascript
const { Client } = require('whatsapp-web.js');
const client = new Client();

client.on('qr', qr => {
    // Scan QR code
});

client.on('ready', () => {
    console.log('Client is ready!');
});

client.on('message', msg => {
    console.log(msg.body);
});

client.initialize();
```

**Limitations**:
- Requires active WhatsApp Web session
- QR code authentication
- Breaks with UI changes
- May violate ToS
- **Account ban risk**

**Not Recommended Because**:
- Against WhatsApp Terms of Service
- Unreliable (breaks with WhatsApp updates)
- Security risks
- No official support

### Option 3: Database Access (Read-Only, Complex)

**Approach**: Access WhatsApp's local database on your device

**Android**:
```bash
# Database location
/data/data/com.whatsapp/databases/msgstore.db

# Requirements:
- Root access OR
- Backup extraction
```

**iOS**:
```bash
# Extract from iTunes/iCloud backup
# Encrypted, requires decryption tools
```

**Steps**:
1. Create device backup
2. Extract WhatsApp data
3. Decrypt database
4. Query with SQLite

**Limitations**:
- Read-only
- Requires device access
- Complex decryption
- Media files separate
- Regular export needed

**Not Practical Because**:
- Requires manual backups
- No real-time access
- Complex setup
- Platform-specific

### Option 4: Alternative Messaging Platforms

**Recommended**: Use platforms with official APIs

#### Telegram
- **Official Bot API**
- Well-documented
- No account restrictions
- Easy to integrate
- Rich features

```python
from telegram import Bot

bot = Bot(token='YOUR_BOT_TOKEN')
messages = bot.get_updates()
```

#### Slack
- Already implemented in Assist-Me
- Official API
- Great for team communication
- See [docs/slack_setup.md](slack_setup.md)

#### Discord
- Official API
- Free
- Good for communities
- Bot-friendly

## Placeholder Tools

The MCP server includes these placeholder tools:

### whatsapp_check_availability

Returns information about WhatsApp integration options.

```python
result = await whatsapp_check_availability()
# Returns detailed info about each approach
```

### whatsapp_placeholder_read_messages

Explains why direct message reading isn't available.

### whatsapp_placeholder_search_messages

Explains search limitations and alternatives.

### whatsapp_placeholder_list_chats

Explains chat listing limitations and alternatives.

## Recommended Approach for Personal Use

If you need to access WhatsApp messages for personal automation:

### Use Email Notifications

1. **Export Chats**:
   - Open WhatsApp
   - Select chat
   - More > Export Chat
   - Choose email or save to Files
   - Process exported text file

2. **Manual Export**:
   - Export important chats weekly
   - Parse text files
   - Store in local database
   - Search/analyze locally

### Sample Export Format

WhatsApp exports look like this:
```
[01/02/2024, 10:30:45] John: Hello!
[01/02/2024, 10:31:12] You: Hi there
[01/02/2024, 10:32:00] John: How are you?
```

### Parsing Exported Chats

```python
import re
from datetime import datetime

def parse_whatsapp_export(file_path):
    messages = []
    pattern = r'\[(\d{2}/\d{2}/\d{4}, \d{2}:\d{2}:\d{2})\] ([^:]+): (.+)'

    with open(file_path, 'r') as f:
        for line in f:
            match = re.match(pattern, line)
            if match:
                timestamp, sender, text = match.groups()
                messages.append({
                    'timestamp': timestamp,
                    'sender': sender,
                    'text': text
                })

    return messages
```

## For Business Use: WhatsApp Business API

If you need official WhatsApp integration:

### Prerequisites
1. Business entity with legal documentation
2. Meta Business Account
3. Phone number (not previously used with WhatsApp)
4. Website/app that will use the API

### Setup Steps

1. **Create Business Account**
   - Go to [Meta Business Suite](https://business.facebook.com/)
   - Create/select business
   - Add WhatsApp Business

2. **Phone Number**
   - Register new number
   - Verify ownership
   - Link to business account

3. **API Access**
   - Apply through Meta Business Suite
   - Wait for approval (can take days/weeks)
   - Get API credentials

4. **Integration**
   ```python
   # Using official SDK
   from whatsapp_business import Client

   client = Client(token='YOUR_BUSINESS_TOKEN')

   # Send template message
   client.send_template(
       to='+1234567890',
       template_name='hello_world'
   )
   ```

### Costs
- Free tier: 1,000 conversations/month
- Paid: Per conversation pricing
- Varies by country

## Privacy & Security Considerations

When considering WhatsApp access:

1. **End-to-End Encryption**: WhatsApp is E2E encrypted; third-party access compromises this
2. **ToS Compliance**: Unofficial methods violate Terms of Service
3. **Account Security**: Risk of account suspension/ban
4. **Data Privacy**: Message content is sensitive personal data
5. **Legal Compliance**: Check local laws regarding message interception

## Future Possibilities

Monitor these developments:

1. **WhatsApp Cloud API**: Expanding business features
2. **Multi-Device**: Improved web/desktop capabilities
3. **Third-Party**: Potential official integrations (unlikely for personal accounts)

## Conclusion

**Current Recommendation**:

For personal use:
- Use manual chat exports
- Consider alternative platforms (Telegram, Slack)
- Leverage existing integrations in Assist-Me

For business use:
- Apply for WhatsApp Business API
- Follow official channels
- Ensure compliance

The placeholder tools in Assist-Me serve as documentation of these options. When official personal APIs become available, full integration can be added.

## Alternative Integrations Already Available

Instead of WhatsApp, use these integrated tools:

1. **iMessage** - For Apple device users ([docs/imessage_setup.md](imessage_setup.md))
2. **Slack** - For team/professional communication ([docs/slack_setup.md](slack_setup.md))
3. **Gmail** - Email communications ([docs/gmail_setup.md](gmail_setup.md))

## References

- [WhatsApp Business API Docs](https://developers.facebook.com/docs/whatsapp)
- [WhatsApp Terms of Service](https://www.whatsapp.com/legal/terms-of-service)
- [Telegram Bot API](https://core.telegram.org/bots/api) (recommended alternative)
- [WhatsApp Web.js](https://github.com/pedroslopez/whatsapp-web.js) (unofficial, use at own risk)
