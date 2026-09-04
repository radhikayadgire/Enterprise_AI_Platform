"""Unit tests for JIRA Tool API integration methods."""

import sys
import os
from unittest.mock import Mock, patch

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def test_jira_tool_initialization_missing_credentials():
    """Test that JIRATool raises error when credentials are missing."""
    print("\nTesting JIRATool initialization with missing credentials...")

    try:
        from tools.jira_tool import JIRATool

        with patch.dict('os.environ', {}, clear=True):
            try:
                tool = JIRATool()
                print("✗ Should have raised ValueError for missing credentials")
                return False
            except ValueError as e:
                if "JIRA credentials not found" in str(e):
                    print(f"✓ Correctly raised ValueError: {e}")
                    return True
                else:
                    print(f"✗ Wrong error message: {e}")
                    return False

    except Exception as e:
        print(f"✗ Initialization test failed: {e}")
        return False


def test_jira_tool_fetch_by_status():
    """Test fetching tickets by status."""
    print("\nTesting JIRATool.fetch_tickets_by_status...")

    try:
        from tools.jira_tool import JIRATool

        # Mock environment variables
        with patch.dict('os.environ', {
            'JIRA_SERVER': 'https://test.atlassian.net',
            'JIRA_EMAIL': 'test@example.com',
            'JIRA_API_TOKEN': 'test_token'
        }):
            # Mock JIRA client
            with patch('tools.jira_tool.JIRA') as mock_jira_class:
                # Create mock issue objects
                mock_issue1 = Mock()
                mock_issue1.id = '1001'
                mock_issue1.key = 'TEST-1'
                mock_issue1.fields.summary = 'First test ticket'
                mock_issue1.fields.description = 'Description of first ticket'
                mock_issue1.fields.status.name = 'In Progress'
                mock_issue1.fields.assignee.displayName = 'John Doe'
                mock_issue1.fields.created = '2026-09-01T10:00:00'
                mock_issue1.fields.updated = '2026-09-04T12:00:00'

                mock_issue2 = Mock()
                mock_issue2.id = '1002'
                mock_issue2.key = 'TEST-2'
                mock_issue2.fields.summary = 'Second test ticket'
                mock_issue2.fields.description = None  # Test null description
                mock_issue2.fields.status.name = 'In Progress'
                mock_issue2.fields.assignee = None  # Test unassigned
                mock_issue2.fields.created = '2026-09-02T10:00:00'
                mock_issue2.fields.updated = '2026-09-03T12:00:00'

                # Mock search_issues return value
                mock_jira = Mock()
                mock_jira.search_issues.return_value = [mock_issue1, mock_issue2]
                mock_jira_class.return_value = mock_jira

                # Create tool and fetch tickets
                tool = JIRATool()
                tickets = tool.fetch_tickets_by_status('In Progress', max_results=50)

                # Verify results
                if len(tickets) != 2:
                    print(f"✗ Expected 2 tickets, got {len(tickets)}")
                    return False

                # Verify first ticket
                if tickets[0]['key'] != 'TEST-1':
                    print(f"✗ Expected key 'TEST-1', got '{tickets[0]['key']}'")
                    return False
                if tickets[0]['summary'] != 'First test ticket':
                    print(f"✗ Wrong summary for TEST-1")
                    return False
                if tickets[0]['assignee'] != 'John Doe':
                    print(f"✗ Wrong assignee for TEST-1")
                    return False

                # Verify second ticket (with null fields)
                if tickets[1]['description'] != 'No description':
                    print(f"✗ Expected 'No description' for null description, got '{tickets[1]['description']}'")
                    return False
                if tickets[1]['assignee'] != 'Unassigned':
                    print(f"✗ Expected 'Unassigned' for null assignee, got '{tickets[1]['assignee']}'")
                    return False

                # Verify JQL query construction
                call_args = mock_jira.search_issues.call_args
                jql_query = call_args[0][0]
                if 'status = "In Progress"' not in jql_query:
                    print(f"✗ Wrong JQL query: {jql_query}")
                    return False

                print("✓ Fetch by status test passed")
                return True

    except Exception as e:
        print(f"✗ Fetch by status test failed: {e}")
        return False


def test_jira_tool_fetch_by_status_with_project():
    """Test fetching tickets by status and project."""
    print("\nTesting JIRATool.fetch_tickets_by_status with project filter...")

    try:
        from tools.jira_tool import JIRATool

        with patch.dict('os.environ', {
            'JIRA_SERVER': 'https://test.atlassian.net',
            'JIRA_EMAIL': 'test@example.com',
            'JIRA_API_TOKEN': 'test_token'
        }):
            with patch('tools.jira_tool.JIRA') as mock_jira_class:
                mock_jira = Mock()
                mock_jira.search_issues.return_value = []
                mock_jira_class.return_value = mock_jira

                tool = JIRATool()
                tickets = tool.fetch_tickets_by_status('Done', project='MYPROJ', max_results=20)

                # Verify JQL includes project filter
                call_args = mock_jira.search_issues.call_args
                jql_query = call_args[0][0]

                if 'project = MYPROJ' not in jql_query:
                    print(f"✗ JQL missing project filter: {jql_query}")
                    return False
                if 'status = "Done"' not in jql_query:
                    print(f"✗ JQL missing status filter: {jql_query}")
                    return False

                # Verify max_results parameter
                if call_args[1]['maxResults'] != 20:
                    print(f"✗ Wrong maxResults: {call_args[1]['maxResults']}")
                    return False

                print("✓ Fetch by status with project test passed")
                return True

    except Exception as e:
        print(f"✗ Fetch by status with project test failed: {e}")
        return False


def test_jira_tool_get_ticket_details():
    """Test getting details for a specific ticket."""
    print("\nTesting JIRATool.get_ticket_details...")

    try:
        from tools.jira_tool import JIRATool

        with patch.dict('os.environ', {
            'JIRA_SERVER': 'https://test.atlassian.net',
            'JIRA_EMAIL': 'test@example.com',
            'JIRA_API_TOKEN': 'test_token'
        }):
            with patch('tools.jira_tool.JIRA') as mock_jira_class:
                # Create detailed mock issue
                mock_issue = Mock()
                mock_issue.id = '2001'
                mock_issue.key = 'PROJ-456'
                mock_issue.fields.summary = 'Critical bug in login'
                mock_issue.fields.description = 'Users cannot login with OAuth'
                mock_issue.fields.status.name = 'In Progress'
                mock_issue.fields.assignee.displayName = 'Jane Smith'
                mock_issue.fields.reporter.displayName = 'Bob Johnson'
                mock_issue.fields.priority.name = 'High'
                mock_issue.fields.created = '2026-09-01T08:00:00'
                mock_issue.fields.updated = '2026-09-04T10:30:00'
                mock_issue.fields.issuetype.name = 'Bug'

                mock_jira = Mock()
                mock_jira.issue.return_value = mock_issue
                mock_jira_class.return_value = mock_jira

                tool = JIRATool()
                ticket = tool.get_ticket_details('PROJ-456')

                # Verify all fields are present
                required_fields = ['id', 'key', 'summary', 'description', 'status',
                                 'assignee', 'reporter', 'priority', 'created', 'updated', 'issue_type']
                for field in required_fields:
                    if field not in ticket:
                        print(f"✗ Missing field: {field}")
                        return False

                # Verify specific values
                if ticket['key'] != 'PROJ-456':
                    print(f"✗ Wrong ticket key: {ticket['key']}")
                    return False
                if ticket['priority'] != 'High':
                    print(f"✗ Wrong priority: {ticket['priority']}")
                    return False
                if ticket['issue_type'] != 'Bug':
                    print(f"✗ Wrong issue type: {ticket['issue_type']}")
                    return False
                if ticket['reporter'] != 'Bob Johnson':
                    print(f"✗ Wrong reporter: {ticket['reporter']}")
                    return False

                # Verify the JIRA API was called with correct ticket key
                mock_jira.issue.assert_called_once_with('PROJ-456')

                print("✓ Get ticket details test passed")
                return True

    except Exception as e:
        print(f"✗ Get ticket details test failed: {e}")
        return False


def test_jira_tool_fetch_by_jql():
    """Test fetching tickets with custom JQL query."""
    print("\nTesting JIRATool.fetch_tickets_by_jql...")

    try:
        from tools.jira_tool import JIRATool

        with patch.dict('os.environ', {
            'JIRA_SERVER': 'https://test.atlassian.net',
            'JIRA_EMAIL': 'test@example.com',
            'JIRA_API_TOKEN': 'test_token'
        }):
            with patch('tools.jira_tool.JIRA') as mock_jira_class:
                # Create mock issue with priority
                mock_issue = Mock()
                mock_issue.id = '3001'
                mock_issue.key = 'TASK-789'
                mock_issue.fields.summary = 'High priority task'
                mock_issue.fields.description = 'Urgent task description'
                mock_issue.fields.status.name = 'To Do'
                mock_issue.fields.assignee.displayName = 'Alice Brown'
                mock_issue.fields.priority.name = 'Critical'
                mock_issue.fields.created = '2026-09-04T09:00:00'
                mock_issue.fields.updated = '2026-09-04T09:30:00'

                mock_jira = Mock()
                mock_jira.search_issues.return_value = [mock_issue]
                mock_jira_class.return_value = mock_jira

                tool = JIRATool()
                custom_jql = 'project = TASK AND priority = Critical AND status = "To Do"'
                tickets = tool.fetch_tickets_by_jql(custom_jql, max_results=100)

                # Verify results include priority field
                if len(tickets) != 1:
                    print(f"✗ Expected 1 ticket, got {len(tickets)}")
                    return False

                if 'priority' not in tickets[0]:
                    print("✗ Priority field missing from JQL results")
                    return False

                if tickets[0]['priority'] != 'Critical':
                    print(f"✗ Wrong priority: {tickets[0]['priority']}")
                    return False

                # Verify exact JQL was used
                call_args = mock_jira.search_issues.call_args
                if call_args[0][0] != custom_jql:
                    print(f"✗ JQL not passed correctly: {call_args[0][0]}")
                    return False

                print("✓ Fetch by JQL test passed")
                return True

    except Exception as e:
        print(f"✗ Fetch by JQL test failed: {e}")
        return False


def test_jira_tool_search_tickets():
    """Test text search functionality."""
    print("\nTesting JIRATool.search_tickets...")

    try:
        from tools.jira_tool import JIRATool

        with patch.dict('os.environ', {
            'JIRA_SERVER': 'https://test.atlassian.net',
            'JIRA_EMAIL': 'test@example.com',
            'JIRA_API_TOKEN': 'test_token'
        }):
            with patch('tools.jira_tool.JIRA') as mock_jira_class:
                mock_jira = Mock()
                mock_jira.search_issues.return_value = []
                mock_jira_class.return_value = mock_jira

                tool = JIRATool()
                tickets = tool.search_tickets('authentication bug', max_results=25)

                # Verify search calls fetch_tickets_by_jql with text query
                call_args = mock_jira.search_issues.call_args
                jql_query = call_args[0][0]

                if 'text ~ "authentication bug"' not in jql_query:
                    print(f"✗ Search didn't create correct JQL: {jql_query}")
                    return False

                print("✓ Search tickets test passed")
                return True

    except Exception as e:
        print(f"✗ Search tickets test failed: {e}")
        return False


def main():
    """Run all JIRA tool tests."""
    print("=" * 70)
    print("JIRA Tool Test Suite")
    print("=" * 70)

    tests = [
        test_jira_tool_initialization_missing_credentials,
        test_jira_tool_fetch_by_status,
        test_jira_tool_fetch_by_status_with_project,
        test_jira_tool_get_ticket_details,
        test_jira_tool_fetch_by_jql,
        test_jira_tool_search_tickets,
    ]

    results = []
    for test in tests:
        try:
            results.append(test())
        except Exception as e:
            print(f"Test {test.__name__} raised exception: {e}")
            results.append(False)

    print("\n" + "=" * 70)
    print(f"Results: {sum(results)}/{len(results)} tests passed")
    print("=" * 70)

    if all(results):
        print("\n✓ All JIRA tool tests passed!")
        return 0
    else:
        print("\n✗ Some tests failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())
