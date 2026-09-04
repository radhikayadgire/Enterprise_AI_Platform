# Enterprise AI Platform - JIRA Integration

A comprehensive Enterprise AI Platform with JIRA integration capabilities, enabling intelligent ticket queries and management through natural language processing.

## Features

- **Natural Language JIRA Queries**: Ask questions about JIRA tickets in plain English using AI-powered agents
- **Status-Based Search**: Fetch tickets filtered by status, project, and other criteria
- **Ticket Details**: Get comprehensive information about specific JIRA tickets
- **JQL Query Support**: Execute custom JIRA Query Language (JQL) queries
- **Text Search**: Search tickets by keywords in summary and description
- **FastAPI Backend**: RESTful API for all JIRA operations
- **Streamlit UI**: User-friendly web interface for interacting with JIRA

## Architecture

```
Enterprise_AI_Platform/
├── agents/
│   ├── jira_agent.py          # LangChain-based AI agent for JIRA queries
│   ├── coordinator.py         # Agent coordinator (to be implemented)
│   ├── email_agent.py         # Email agent (to be implemented)
│   └── hr_agent.py            # HR agent (to be implemented)
├── backend/
│   └── main.py                # FastAPI backend server
├── tools/
│   ├── jira_tool.py           # JIRA API integration tool
│   ├── email_tool.py          # Email tool (to be implemented)
│   ├── hr_tool.py             # HR tool (to be implemented)
│   └── search_tool.py         # Search tool (to be implemented)
├── ui/
│   └── app.py                 # Streamlit web interface
├── data/                      # Data files
├── .env                       # Environment configuration
└── requirements.txt           # Python dependencies
```

## Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Environment Variables

Edit the `.env` file with your credentials:

```env
# OpenAI Configuration (required for AI agent)
OPENAI_API_KEY=your_openai_api_key_here

# JIRA Configuration
JIRA_SERVER=https://your-domain.atlassian.net
JIRA_EMAIL=your-email@example.com
JIRA_API_TOKEN=your_jira_api_token_here
```

**Getting JIRA API Token:**
1. Go to https://id.atlassian.com/manage-profile/security/api-tokens
2. Click "Create API token"
3. Give it a name and copy the token
4. Paste it into the `.env` file

### 3. Start the Backend Server

```bash
# From the project root directory
python backend/main.py

# Or using uvicorn directly
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000`
- API Documentation: `http://localhost:8000/docs`
- Health Check: `http://localhost:8000/health`

### 4. Start the UI

```bash
# In a new terminal
streamlit run ui/app.py
```

The web interface will open at `http://localhost:8501`

## Usage

### Web Interface

1. **Natural Language Query**: Ask questions like:
   - "Fetch the descriptions and IDs of all tickets with status 'in progress'"
   - "Show me high priority bugs"
   - "What tickets are assigned to me?"

2. **Status-Based Search**: Filter tickets by status and optionally by project

3. **Ticket Details**: Look up specific tickets by their key (e.g., PROJ-123)

4. **JQL Query**: Execute custom JQL queries for advanced filtering

5. **Text Search**: Search tickets by keywords

### API Endpoints

#### Natural Language Query
```bash
curl -X POST "http://localhost:8000/jira/query" \
  -H "Content-Type: application/json" \
  -d '{"query": "Fetch all tickets with status in progress"}'
```

#### Fetch by Status
```bash
curl -X POST "http://localhost:8000/jira/status" \
  -H "Content-Type: application/json" \
  -d '{"status": "In Progress", "max_results": 50}'
```

#### Get Ticket Details
```bash
curl "http://localhost:8000/jira/ticket/PROJ-123"
```

#### Search Tickets
```bash
curl -X POST "http://localhost:8000/jira/search" \
  -H "Content-Type: application/json" \
  -d '{"query": "authentication bug", "max_results": 50}'
```

#### Execute JQL Query
```bash
curl -X POST "http://localhost:8000/jira/jql" \
  -H "Content-Type: application/json" \
  -d '{"jql": "project = PROJ AND status = \"In Progress\"", "max_results": 50}'
```

## Python Usage

### Using the JIRA Tool Directly

```python
from tools.jira_tool import JIRATool

# Initialize
jira = JIRATool()

# Fetch tickets by status
tickets = jira.fetch_tickets_by_status("In Progress", max_results=10)

# Search tickets
results = jira.search_tickets("authentication")

# Get ticket details
ticket = jira.get_ticket_details("PROJ-123")

# Execute JQL query
tickets = jira.fetch_tickets_by_jql('status = "In Progress" AND priority = High')
```

### Using the JIRA Agent (AI-Powered)

```python
from agents.jira_agent import JIRAAgent

# Initialize
agent = JIRAAgent()

# Process natural language queries
response = agent.process_query("What are the high priority bugs in the PROJ project?")
print(response)
```

## Examples

### Example 1: Fetch In-Progress Tickets
**Query:** "Fetch the descriptions and IDs of all tickets with status 'in progress'"

**Response:**
```
Found 5 ticket(s) with status 'In Progress':

- PROJ-101: Implement user authentication
  Status: In Progress, Assignee: John Doe
  Description: Add JWT-based authentication to the API...

- PROJ-102: Fix database connection pooling
  Status: In Progress, Assignee: Jane Smith
  Description: Optimize connection pool settings for better performance...
```

### Example 2: JQL Query for High Priority Bugs
**Query:**
```jql
project = PROJ AND status = "In Progress" AND priority = High AND type = Bug
```

## Testing

Run the validation suite:

```bash
# Install test dependencies (if not already installed)
pip install pytest pytest-asyncio httpx

# Run tests (to be implemented)
pytest
```

## Troubleshooting

### JIRA Connection Issues

1. **503 Service Unavailable**: Check that JIRA credentials are properly set in `.env`
2. **401 Unauthorized**: Verify your JIRA email and API token are correct
3. **Connection timeout**: Ensure your JIRA server URL is correct and accessible

### Backend Not Starting

1. Check that port 8000 is not already in use
2. Verify all dependencies are installed: `pip install -r requirements.txt`
3. Check the console output for specific error messages

### UI Not Loading

1. Ensure the backend is running first
2. Check that port 8501 is available
3. Try accessing `http://localhost:8501` directly in your browser

## Future Enhancements

- [ ] Implement coordinator agent for multi-agent orchestration
- [ ] Add email notification capabilities
- [ ] Integrate HR system tools
- [ ] Add ticket creation and update capabilities
- [ ] Implement caching for improved performance
- [ ] Add authentication and authorization
- [ ] Deploy to cloud platforms (AWS, Azure, GCP)

## License

MIT License

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
