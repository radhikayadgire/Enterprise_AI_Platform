"""JIRA integration tool for fetching and managing JIRA tickets."""

import os
from typing import List, Dict, Any, Optional
from jira import JIRA
from jira.exceptions import JIRAError
from dotenv import load_dotenv

load_dotenv()


class JIRATool:
    """Tool for interacting with JIRA API."""

    def __init__(self):
        """Initialize JIRA connection."""
        self.jira_server = os.getenv("JIRA_SERVER")
        self.jira_email = os.getenv("JIRA_EMAIL")
        self.jira_api_token = os.getenv("JIRA_API_TOKEN")

        if not all([self.jira_server, self.jira_email, self.jira_api_token]):
            raise ValueError(
                "JIRA credentials not found. Please set JIRA_SERVER, "
                "JIRA_EMAIL, and JIRA_API_TOKEN in .env file"
            )

        try:
            self.jira = JIRA(
                server=self.jira_server,
                basic_auth=(self.jira_email, self.jira_api_token)
            )
        except JIRAError as e:
            raise ConnectionError(f"Failed to connect to JIRA: {str(e)}")

    def fetch_tickets_by_status(
        self,
        status: str,
        max_results: int = 50,
        project: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Fetch JIRA tickets by status.

        Args:
            status: The status to filter by (e.g., 'In Progress', 'Done')
            max_results: Maximum number of results to return
            project: Optional project key to filter by

        Returns:
            List of ticket dictionaries with id, key, summary, description, status
        """
        try:
            # Build JQL query
            jql = f'status = "{status}"'
            if project:
                jql = f'project = {project} AND {jql}'

            # Fetch issues
            issues = self.jira.search_issues(
                jql,
                maxResults=max_results,
                fields='summary,description,status,assignee,created,updated'
            )

            # Format results
            tickets = []
            for issue in issues:
                tickets.append({
                    'id': issue.id,
                    'key': issue.key,
                    'summary': issue.fields.summary,
                    'description': issue.fields.description or 'No description',
                    'status': issue.fields.status.name,
                    'assignee': issue.fields.assignee.displayName if issue.fields.assignee else 'Unassigned',
                    'created': str(issue.fields.created),
                    'updated': str(issue.fields.updated)
                })

            return tickets

        except JIRAError as e:
            raise Exception(f"Error fetching JIRA tickets: {str(e)}")

    def fetch_tickets_by_jql(
        self,
        jql_query: str,
        max_results: int = 50
    ) -> List[Dict[str, Any]]:
        """
        Fetch JIRA tickets using custom JQL query.

        Args:
            jql_query: JQL query string
            max_results: Maximum number of results to return

        Returns:
            List of ticket dictionaries
        """
        try:
            issues = self.jira.search_issues(
                jql_query,
                maxResults=max_results,
                fields='summary,description,status,assignee,created,updated,priority'
            )

            tickets = []
            for issue in issues:
                tickets.append({
                    'id': issue.id,
                    'key': issue.key,
                    'summary': issue.fields.summary,
                    'description': issue.fields.description or 'No description',
                    'status': issue.fields.status.name,
                    'assignee': issue.fields.assignee.displayName if issue.fields.assignee else 'Unassigned',
                    'priority': issue.fields.priority.name if issue.fields.priority else 'None',
                    'created': str(issue.fields.created),
                    'updated': str(issue.fields.updated)
                })

            return tickets

        except JIRAError as e:
            raise Exception(f"Error executing JQL query: {str(e)}")

    def get_ticket_details(self, ticket_key: str) -> Dict[str, Any]:
        """
        Get detailed information about a specific ticket.

        Args:
            ticket_key: JIRA ticket key (e.g., 'PROJ-123')

        Returns:
            Dictionary with ticket details
        """
        try:
            issue = self.jira.issue(ticket_key)

            return {
                'id': issue.id,
                'key': issue.key,
                'summary': issue.fields.summary,
                'description': issue.fields.description or 'No description',
                'status': issue.fields.status.name,
                'assignee': issue.fields.assignee.displayName if issue.fields.assignee else 'Unassigned',
                'reporter': issue.fields.reporter.displayName if issue.fields.reporter else 'Unknown',
                'priority': issue.fields.priority.name if issue.fields.priority else 'None',
                'created': str(issue.fields.created),
                'updated': str(issue.fields.updated),
                'issue_type': issue.fields.issuetype.name
            }

        except JIRAError as e:
            raise Exception(f"Error fetching ticket {ticket_key}: {str(e)}")

    def search_tickets(
        self,
        search_text: str,
        max_results: int = 50
    ) -> List[Dict[str, Any]]:
        """
        Search for tickets containing specific text.

        Args:
            search_text: Text to search for in summary and description
            max_results: Maximum number of results to return

        Returns:
            List of matching tickets
        """
        try:
            jql = f'text ~ "{search_text}"'
            return self.fetch_tickets_by_jql(jql, max_results)

        except Exception as e:
            raise Exception(f"Error searching tickets: {str(e)}")


# Convenience function for quick access
def get_jira_tool() -> JIRATool:
    """Get initialized JIRA tool instance."""
    return JIRATool()
