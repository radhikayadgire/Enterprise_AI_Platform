"""FastAPI backend for Enterprise AI Platform with JIRA integration."""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.jira_agent import JIRAAgent
from tools.jira_tool import JIRATool

app = FastAPI(
    title="Enterprise AI Platform API",
    description="API for JIRA integration and AI-powered ticket analysis",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize JIRA components
jira_tool = None
jira_agent = None


@app.on_event("startup")
async def startup_event():
    """Initialize JIRA components on startup."""
    global jira_tool, jira_agent
    try:
        jira_tool = JIRATool()
        jira_agent = JIRAAgent()
    except Exception as e:
        print(f"Warning: JIRA initialization failed: {str(e)}")
        print("JIRA endpoints will return errors until credentials are configured.")


# Pydantic models
class JIRAQuery(BaseModel):
    """Model for JIRA query request."""
    query: str
    max_results: Optional[int] = 50


class StatusQuery(BaseModel):
    """Model for status-based query."""
    status: str
    project: Optional[str] = None
    max_results: Optional[int] = 50


class JQLQuery(BaseModel):
    """Model for JQL query."""
    jql: str
    max_results: Optional[int] = 50


class TicketKey(BaseModel):
    """Model for ticket key request."""
    key: str


# API Endpoints
@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Enterprise AI Platform API",
        "version": "1.0.0",
        "endpoints": {
            "/docs": "API documentation",
            "/jira/query": "Natural language JIRA query",
            "/jira/status": "Fetch tickets by status",
            "/jira/ticket/{key}": "Get ticket details",
            "/jira/search": "Search tickets",
            "/jira/jql": "Execute JQL query"
        }
    }


@app.post("/jira/query")
async def query_jira(query_data: JIRAQuery) -> Dict[str, Any]:
    """
    Process natural language query about JIRA tickets using AI agent.

    Example queries:
    - "Fetch all tickets with status 'in progress'"
    - "Show me high priority bugs"
    - "What tickets are assigned to me?"
    """
    if not jira_agent:
        raise HTTPException(
            status_code=503,
            detail="JIRA agent not initialized. Check JIRA credentials in .env file."
        )

    try:
        response = jira_agent.process_query(query_data.query)
        return {
            "query": query_data.query,
            "response": response,
            "status": "success"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/jira/status")
async def get_tickets_by_status(status_query: StatusQuery) -> Dict[str, Any]:
    """
    Fetch JIRA tickets by status.

    Args:
        status: Status to filter by (e.g., "In Progress", "Done", "To Do")
        project: Optional project key to filter by
        max_results: Maximum number of results (default: 50)
    """
    if not jira_tool:
        raise HTTPException(
            status_code=503,
            detail="JIRA tool not initialized. Check JIRA credentials in .env file."
        )

    try:
        tickets = jira_tool.fetch_tickets_by_status(
            status=status_query.status,
            max_results=status_query.max_results,
            project=status_query.project
        )
        return {
            "status": status_query.status,
            "count": len(tickets),
            "tickets": tickets
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/jira/ticket/{ticket_key}")
async def get_ticket_details(ticket_key: str) -> Dict[str, Any]:
    """
    Get detailed information about a specific JIRA ticket.

    Args:
        ticket_key: JIRA ticket key (e.g., "PROJ-123")
    """
    if not jira_tool:
        raise HTTPException(
            status_code=503,
            detail="JIRA tool not initialized. Check JIRA credentials in .env file."
        )

    try:
        ticket = jira_tool.get_ticket_details(ticket_key)
        return ticket
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))


@app.post("/jira/search")
async def search_tickets(query_data: JIRAQuery) -> Dict[str, Any]:
    """
    Search for JIRA tickets containing specific text.

    Args:
        query: Text to search for in ticket summary and description
        max_results: Maximum number of results (default: 50)
    """
    if not jira_tool:
        raise HTTPException(
            status_code=503,
            detail="JIRA tool not initialized. Check JIRA credentials in .env file."
        )

    try:
        tickets = jira_tool.search_tickets(
            search_text=query_data.query,
            max_results=query_data.max_results
        )
        return {
            "search_query": query_data.query,
            "count": len(tickets),
            "tickets": tickets
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/jira/jql")
async def execute_jql(jql_query: JQLQuery) -> Dict[str, Any]:
    """
    Execute a custom JQL (JIRA Query Language) query.

    Args:
        jql: JQL query string (e.g., "project = PROJ AND status = 'In Progress'")
        max_results: Maximum number of results (default: 50)
    """
    if not jira_tool:
        raise HTTPException(
            status_code=503,
            detail="JIRA tool not initialized. Check JIRA credentials in .env file."
        )

    try:
        tickets = jira_tool.fetch_tickets_by_jql(
            jql_query=jql_query.jql,
            max_results=jql_query.max_results
        )
        return {
            "jql": jql_query.jql,
            "count": len(tickets),
            "tickets": tickets
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "jira_tool_initialized": jira_tool is not None,
        "jira_agent_initialized": jira_agent is not None
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
