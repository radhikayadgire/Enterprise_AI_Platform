"""JIRA Agent for intelligent JIRA ticket queries and analysis."""

import os
import re
from typing import List, Dict, Any, Optional, Tuple
from dotenv import load_dotenv
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from tools.jira_tool import JIRATool

load_dotenv()


class JIRAAgent:
    """Agent for handling JIRA-related queries using LangChain."""

    def __init__(self):
        """Initialize the JIRA agent with tools."""
        self.jira_tool = JIRATool()

    def _parse_query_intent(self, query: str) -> Tuple[str, str]:
        """
        Parse query to determine intent and extract parameters.

        Returns:
            Tuple of (intent, parameter)
        """
        query_lower = query.lower()

        # Status-based query
        status_patterns = [
            r'status\s+["\']?([a-z\s]+)["\']?',
            r'with status\s+["\']?([a-z\s]+)["\']?',
            r'tickets?\s+(?:that are\s+)?(?:in\s+)?["\']?([a-z\s]+)["\']?\s+(?:status)?',
        ]

        for pattern in status_patterns:
            match = re.search(pattern, query_lower)
            if match:
                status = match.group(1).strip()
                return ("fetch_by_status", status)

        # Ticket key lookup
        ticket_key_pattern = r'\b([A-Z]+-\d+)\b'
        match = re.search(ticket_key_pattern, query)
        if match:
            return ("get_ticket_details", match.group(1))

        # Default to search
        return ("search", query)

    def _create_agent(self):
        """Compatibility method - no longer creates AgentExecutor."""
        pass

    def _fetch_by_status_wrapper(self, status: str) -> str:
        """Wrapper for fetch_tickets_by_status tool."""
        try:
            tickets = self.jira_tool.fetch_tickets_by_status(status)
            if not tickets:
                return f"No tickets found with status '{status}'"

            result = f"Found {len(tickets)} ticket(s) with status '{status}':\n\n"
            for ticket in tickets:
                result += f"- {ticket['key']}: {ticket['summary']}\n"
                result += f"  Status: {ticket['status']}, Assignee: {ticket['assignee']}\n"
                result += f"  Description: {ticket['description'][:100]}...\n\n"

            return result
        except Exception as e:
            return f"Error fetching tickets: {str(e)}"

    def _search_tickets_wrapper(self, search_text: str) -> str:
        """Wrapper for search_tickets tool."""
        try:
            tickets = self.jira_tool.search_tickets(search_text)
            if not tickets:
                return f"No tickets found matching '{search_text}'"

            result = f"Found {len(tickets)} ticket(s) matching '{search_text}':\n\n"
            for ticket in tickets:
                result += f"- {ticket['key']}: {ticket['summary']}\n"
                result += f"  Status: {ticket['status']}\n\n"

            return result
        except Exception as e:
            return f"Error searching tickets: {str(e)}"

    def _get_ticket_details_wrapper(self, ticket_key: str) -> str:
        """Wrapper for get_ticket_details tool."""
        try:
            ticket = self.jira_tool.get_ticket_details(ticket_key)

            result = f"Ticket Details for {ticket['key']}:\n\n"
            result += f"Summary: {ticket['summary']}\n"
            result += f"Status: {ticket['status']}\n"
            result += f"Assignee: {ticket['assignee']}\n"
            result += f"Priority: {ticket['priority']}\n"
            result += f"Type: {ticket['issue_type']}\n"
            result += f"Created: {ticket['created']}\n"
            result += f"Updated: {ticket['updated']}\n"
            result += f"\nDescription:\n{ticket['description']}\n"

            return result
        except Exception as e:
            return f"Error fetching ticket details: {str(e)}"

    def _fetch_by_jql_wrapper(self, jql_query: str) -> str:
        """Wrapper for fetch_by_jql tool."""
        try:
            tickets = self.jira_tool.fetch_tickets_by_jql(jql_query)
            if not tickets:
                return f"No tickets found for JQL query: {jql_query}"

            result = f"Found {len(tickets)} ticket(s):\n\n"
            for ticket in tickets:
                result += f"- {ticket['key']}: {ticket['summary']}\n"
                result += f"  Status: {ticket['status']}, Priority: {ticket['priority']}\n\n"

            return result
        except Exception as e:
            return f"Error executing JQL query: {str(e)}"

    def process_query(self, query: str) -> str:
        """
        Process a natural language query about JIRA tickets.

        Args:
            query: Natural language query about JIRA tickets

        Returns:
            Formatted response with ticket information
        """
        try:
            # Parse intent
            intent, parameter = self._parse_query_intent(query)

            # Execute appropriate method
            if intent == "fetch_by_status":
                return self._fetch_by_status_wrapper(parameter)
            elif intent == "get_ticket_details":
                return self._get_ticket_details_wrapper(parameter)
            elif intent == "search":
                return self._search_tickets_wrapper(parameter)
            else:
                return "Unable to understand the query. Please try rephrasing."

        except Exception as e:
            return f"Error processing query: {str(e)}"


# Convenience function
def get_jira_agent() -> JIRAAgent:
    """Get initialized JIRA agent instance."""
    return JIRAAgent()
