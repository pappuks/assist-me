# Assist-Me System Prompts

This directory contains comprehensive system prompts for various use cases supported by the Assist-Me MCP server. Each prompt provides detailed instructions on how an AI assistant should use the available MCP tools to accomplish specific tasks.

## Available Prompts

### 1. [Calendar Assistant](calendar_assistant.md)
**Use Case**: Create calendar entries by analyzing emails, messages, and notes

**Key Capabilities**:
- Multi-source event detection (Gmail, iMessage, Slack, Mac Notes)
- Intelligent event extraction (date, time, location, attendees)
- Automatic calendar event creation
- Conflict detection and resolution

**Primary MCP Tools Used**:
- `gmail_search`, `gmail_get_message`
- `slack_search_messages`, `slack_read_messages`
- `imessage_search_messages`, `imessage_read_messages`
- `notes_search_notes`, `notes_read_note`
- `calendar_list_events`, `calendar_create_event`, `calendar_update_event`

**Example Query**: "Check my emails and messages for any meeting requests this week and add them to my calendar"

---

### 2. [To-Do List Generator](todo_list_generator.md)
**Use Case**: Generate weekly/daily to-do lists from your communications

**Key Capabilities**:
- Task identification from emails, messages, and notes
- Smart categorization and prioritization
- Time estimation and deadline tracking
- Daily and weekly to-do list generation

**Primary MCP Tools Used**:
- `gmail_search`, `gmail_list_messages`
- `slack_search_messages`, `slack_read_messages`
- `imessage_read_messages`
- `notes_search_notes`, `notes_list_notes`
- `calendar_list_events`

**Example Query**: "Create my to-do list for this week based on all my emails and messages"

---

### 3. [Meal Planner](meal_planner.md)
**Use Case**: Prepare meal plans for the week

**Key Capabilities**:
- Dietary preference discovery
- Schedule-based meal complexity matching
- Weekly meal plan generation with recipes
- Organized shopping lists with budget estimates
- Meal prep optimization

**Primary MCP Tools Used**:
- `notes_search_notes`, `notes_read_note` (recipes, preferences)
- `gmail_search` (recipe newsletters, meal kits)
- `imessage_read_messages` (family food discussions)
- `calendar_list_events` (schedule analysis)
- `calendar_create_event` (meal prep reminders)

**Example Query**: "Create a healthy meal plan for next week based on my dietary preferences and schedule"

---

### 4. [Kids' Schedule Organizer](kids_schedule_organizer.md)
**Use Case**: Organize kids' study schedules and school activities

**Key Capabilities**:
- School schedule management
- Homework assignment tracking
- Extracurricular activity coordination
- Test preparation planning
- Balanced schedule creation

**Primary MCP Tools Used**:
- `gmail_search` (teacher emails, school notifications)
- `imessage_read_messages` (family communications)
- `notes_search_notes` (school schedules, homework tracking)
- `slack_read_messages` (parent group communications)
- `calendar_list_events`, `calendar_create_event`

**Example Query**: "Organize my kids' schedules for the week including homework, soccer practice, and piano lessons"

---

### 5. [Travel Planner](travel_planner.md)
**Use Case**: Plan and organize travel itineraries

**Key Capabilities**:
- Travel booking extraction (flights, hotels, activities)
- Day-by-day itinerary creation
- Packing list generation
- Budget tracking
- Pre-departure checklist creation

**Primary MCP Tools Used**:
- `gmail_search`, `gmail_get_message` (confirmations)
- `imessage_read_messages` (travel planning discussions)
- `notes_search_notes` (travel notes, research)
- `calendar_list_events`, `calendar_create_event`

**Example Query**: "Create a complete itinerary for my Paris trip next month from all my booking confirmations"

---

### 6. [Amazon Orders & Deliveries Tracker](amazon_tracker.md)
**Use Case**: Track Amazon orders and deliveries

**Key Capabilities**:
- Order confirmation parsing
- Shipment tracking
- Delivery date monitoring
- Package status updates
- Spending summaries

**Primary MCP Tools Used**:
- `gmail_search`, `gmail_get_message` (Amazon emails)
- `amazon_search_orders`, `amazon_get_deliveries`, `amazon_parse_order_emails`
- `calendar_create_event` (delivery reminders)

**Example Query**: "Show me all my Amazon packages arriving this week and create calendar reminders"

---

### 7. [Communication Search](communication_search.md)
**Use Case**: Search across all your communication channels

**Key Capabilities**:
- Multi-platform unified search
- Intelligent query understanding
- Relevance ranking across sources
- Timeline and context preservation
- Action item extraction

**Primary MCP Tools Used**:
- `gmail_search`, `gmail_get_message`
- `slack_search_messages`, `slack_read_messages`, `slack_get_thread`
- `imessage_search_messages`, `imessage_read_messages`
- `notes_search_notes`, `notes_read_note`

**Example Query**: "Find everything about the budget proposal across all my communications"

---

## How to Use These Prompts

### For AI Model Configuration

If you're using these prompts with an AI model or LLM:

1. **Select the appropriate prompt** for your use case
2. **Copy the entire content** of the markdown file
3. **Use it as the system prompt** when configuring your AI assistant
4. **Provide user queries** that match the use case

### For Integration with Assist-Me

These prompts are designed to work with the Assist-Me MCP server. The AI assistant will:

1. **Receive the system prompt** defining its role and capabilities
2. **Accept user queries** related to the use case
3. **Execute MCP tool calls** to gather information from your data sources
4. **Process and organize** the retrieved information
5. **Present results** in the formats specified in each prompt

### Example Integration

```python
from mcp.client import Client

# Initialize MCP client
client = Client("http://localhost:8080/mcp")

# Load system prompt
with open("prompts/calendar_assistant.md", "r") as f:
    system_prompt = f.read()

# Configure AI with system prompt
assistant = AI(system_prompt=system_prompt, mcp_client=client)

# User query
result = assistant.query("Find meeting requests from this week and add to calendar")
```

### Combining Prompts

Some prompts integrate well together:

- **Calendar Assistant + To-Do List Generator**: Events inform task scheduling
- **Travel Planner + Calendar Assistant**: Travel bookings become calendar events
- **Amazon Tracker + Calendar Assistant**: Deliveries become calendar reminders
- **Communication Search + All Others**: Search provides data for all other use cases

---

## Customization

Each prompt can be customized for specific needs:

### Adjusting Search Timeframes

Most prompts use default timeframes (e.g., "past 7 days", "past 30 days"). You can modify these in the prompt:

```
# Original
gmail_search(query="meeting after:7d", max_results=20)

# Customized for 14 days
gmail_search(query="meeting after:14d", max_results=20)
```

### Adding Domain-Specific Keywords

Tailor search queries to your domain:

```
# For medical professionals
keywords = ["patient", "appointment", "consultation", "procedure"]

# For software developers
keywords = ["deployment", "bug", "feature", "sprint", "standup"]
```

### Modifying Output Formats

Adjust the response format sections to match your preferred style:
- Change markdown formatting
- Adjust verbosity levels
- Modify grouping and categorization
- Customize emoji usage

---

## Best Practices

### 1. Context Preservation
All prompts emphasize preserving context when retrieving information. Always include:
- Source attribution (which email, message, note)
- Timestamps
- Related conversations or threads

### 2. Privacy & Security
Be mindful of:
- Sensitive information in communications
- Personal data in notes
- Confidential business information
- Always ask for confirmation before sharing or creating entries with sensitive data

### 3. Error Handling
Prompts include guidance on handling:
- Missing information
- Ambiguous dates or times
- Conflicting data
- API failures or rate limits

### 4. User Confirmation
Important actions should request confirmation:
- Creating calendar events with external attendees
- Large financial transactions (travel bookings)
- Significant time commitments
- Private or sensitive information

---

## Prompt Structure

Each prompt follows a consistent structure:

1. **Role Definition**: Clear description of the assistant's purpose
2. **Core Capabilities**: What the assistant can do
3. **MCP Tools Usage**: Detailed instructions on using each relevant tool
4. **Output Structure**: Examples of formatted responses
5. **Operational Guidelines**: Rules and best practices
6. **Example Workflows**: Step-by-step processes for common tasks
7. **Integration Points**: How to work with other prompts
8. **Success Metrics**: How to measure effectiveness

---

## Contributing

To create a new prompt or improve an existing one:

1. **Follow the standard structure** outlined above
2. **Include comprehensive examples** of MCP tool usage
3. **Provide multiple workflow scenarios**
4. **Define clear output formats** with markdown examples
5. **Consider edge cases** and error handling
6. **Test with real data** from the MCP server

---

## Version History

- **v1.0** (January 2024) - Initial release with 7 core prompts
  - Calendar Assistant
  - To-Do List Generator
  - Meal Planner
  - Kids' Schedule Organizer
  - Travel Planner
  - Amazon Tracker
  - Communication Search

---

## Support & Feedback

For questions or suggestions about these prompts:

- Open an issue on GitHub
- Contribute improvements via pull requests
- Share your custom prompts with the community

---

## License

These prompts are part of the Assist-Me project and are licensed under the same MIT License.

---

Built with ❤️ using [Claude Code](https://claude.com/claude-code) and the Model Context Protocol.
