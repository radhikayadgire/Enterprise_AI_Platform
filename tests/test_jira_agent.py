"""Unit tests for JIRA Agent query parsing and processing."""

import sys
import os
from unittest.mock import Mock, patch

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def test_agent_parse_status_query():
    """Test parsing of status-based queries."""
    print("\nTesting agent status query parsing...")

    try:
        from agents.jira_agent import JIRAAgent

        # Mock the JIRATool to avoid requiring JIRA credentials
        with patch('agents.jira_agent.JIRATool') as mock_tool:
            mock_tool.return_value = Mock()
            agent = JIRAAgent()

            # Test various status query formats
            test_cases = [
                ("Fetch tickets with status 'In Progress'", ("fetch_by_status", "in progress")),
                ("Show me tickets with status 'Done'", ("fetch_by_status", "done")),
                ("Get all tickets in 'To Do' status", ("fetch_by_status", "to do")),
                ("tickets that are in progress", ("fetch_by_status", "in progress")),
            ]

            for query, expected in test_cases:
                intent, param = agent._parse_query_intent(query)
                if intent != expected[0]:
                    print(f"✗ Failed: '{query}' -> Got intent '{intent}', expected '{expected[0]}'")
                    return False
                if param != expected[1]:
                    print(f"✗ Failed: '{query}' -> Got param '{param}', expected '{expected[1]}'")
                    return False
                print(f"✓ Parsed: '{query}' -> ({intent}, '{param}')")

            print("✓ All status query parsing tests passed")
            return True

    except Exception as e:
        print(f"✗ Status query parsing test failed: {e}")
        return False


def test_agent_parse_ticket_key_query():
    """Test parsing of ticket key lookup queries."""
    print("\nTesting agent ticket key query parsing...")

    try:
        from agents.jira_agent import JIRAAgent

        with patch('agents.jira_agent.JIRATool') as mock_tool:
            mock_tool.return_value = Mock()
            agent = JIRAAgent()

            test_cases = [
                ("Show me ticket PROJ-123", ("get_ticket_details", "PROJ-123")),
                ("Get details for ABC-456", ("get_ticket_details", "ABC-456")),
                ("What's the status of TASK-789", ("get_ticket_details", "TASK-789")),
            ]

            for query, expected in test_cases:
                intent, param = agent._parse_query_intent(query)
                if intent != expected[0] or param != expected[1]:
                    print(f"✗ Failed: '{query}' -> Got ({intent}, '{param}'), expected {expected}")
                    return False
                print(f"✓ Parsed: '{query}' -> ({intent}, '{param}')")

            print("✓ All ticket key parsing tests passed")
            return True

    except Exception as e:
        print(f"✗ Ticket key parsing test failed: {e}")
        return False


def test_agent_parse_search_query():
    """Test parsing of search queries (default fallback)."""
    print("\nTesting agent search query parsing...")

    try:
        from agents.jira_agent import JIRAAgent

        with patch('agents.jira_agent.JIRATool') as mock_tool:
            mock_tool.return_value = Mock()
            agent = JIRAAgent()

            test_cases = [
                ("authentication bugs", ("search", "authentication bugs")),
                ("Find tickets about login issues", ("search", "Find tickets about login issues")),
                ("memory leak in production", ("search", "memory leak in production")),
            ]

            for query, expected in test_cases:
                intent, param = agent._parse_query_intent(query)
                if intent != expected[0] or param != expected[1]:
                    print(f"✗ Failed: '{query}' -> Got ({intent}, '{param}'), expected {expected}")
                    return False
                print(f"✓ Parsed: '{query}' -> ({intent}, '{param}')")

            print("✓ All search query parsing tests passed")
            return True

    except Exception as e:
        print(f"✗ Search query parsing test failed: {e}")
        return False


def test_agent_process_query_status():
    """Test end-to-end query processing for status queries."""
    print("\nTesting agent process_query for status...")

    try:
        from agents.jira_agent import JIRAAgent

        with patch('agents.jira_agent.JIRATool') as mock_tool_class:
            # Mock the JIRATool instance and its method
            mock_tool = Mock()
            mock_tool.fetch_tickets_by_status.return_value = [
                {
                    'key': 'TEST-1',
                    'summary': 'Test ticket 1',
                    'status': 'In Progress',
                    'assignee': 'John Doe',
                    'description': 'This is a test ticket description'
                },
                {
                    'key': 'TEST-2',
                    'summary': 'Test ticket 2',
                    'status': 'In Progress',
                    'assignee': 'Jane Smith',
                    'description': 'Another test ticket'
                }
            ]
            mock_tool_class.return_value = mock_tool

            agent = JIRAAgent()
            response = agent.process_query("Fetch tickets with status 'In Progress'")

            # Verify response contains expected elements
            if "Found 2 ticket(s)" not in response:
                print(f"✗ Response missing ticket count: {response}")
                return False
            if "TEST-1" not in response or "TEST-2" not in response:
                print(f"✗ Response missing ticket keys: {response}")
                return False
            if "Test ticket 1" not in response:
                print(f"✗ Response missing ticket summary: {response}")
                return False

            # Verify the tool was called correctly
            mock_tool.fetch_tickets_by_status.assert_called_once_with('in progress')

            print("✓ Process query for status test passed")
            return True

    except Exception as e:
        print(f"✗ Process query status test failed: {e}")
        return False


def test_agent_process_query_ticket_details():
    """Test end-to-end query processing for ticket details."""
    print("\nTesting agent process_query for ticket details...")

    try:
        from agents.jira_agent import JIRAAgent

        with patch('agents.jira_agent.JIRATool') as mock_tool_class:
            mock_tool = Mock()
            mock_tool.get_ticket_details.return_value = {
                'key': 'PROJ-123',
                'summary': 'Fix login bug',
                'status': 'In Progress',
                'assignee': 'John Doe',
                'priority': 'High',
                'issue_type': 'Bug',
                'created': '2026-09-01',
                'updated': '2026-09-04',
                'description': 'Users cannot login with SSO'
            }
            mock_tool_class.return_value = mock_tool

            agent = JIRAAgent()
            response = agent.process_query("Show me ticket PROJ-123")

            # Verify response contains ticket details
            if "PROJ-123" not in response:
                print(f"✗ Response missing ticket key: {response}")
                return False
            if "Fix login bug" not in response:
                print(f"✗ Response missing summary: {response}")
                return False
            if "High" not in response:
                print(f"✗ Response missing priority: {response}")
                return False

            mock_tool.get_ticket_details.assert_called_once_with('PROJ-123')

            print("✓ Process query for ticket details test passed")
            return True

    except Exception as e:
        print(f"✗ Process query ticket details test failed: {e}")
        return False


def test_agent_process_query_no_results():
    """Test query processing when no tickets are found."""
    print("\nTesting agent process_query with no results...")

    try:
        from agents.jira_agent import JIRAAgent

        with patch('agents.jira_agent.JIRATool') as mock_tool_class:
            mock_tool = Mock()
            mock_tool.fetch_tickets_by_status.return_value = []
            mock_tool_class.return_value = mock_tool

            agent = JIRAAgent()
            response = agent.process_query("Fetch tickets with status 'Nonexistent'")

            if "No tickets found" not in response:
                print(f"✗ Response should indicate no tickets found: {response}")
                return False

            print("✓ No results handling test passed")
            return True

    except Exception as e:
        print(f"✗ No results test failed: {e}")
        return False


def main():
    """Run all JIRA agent tests."""
    print("=" * 70)
    print("JIRA Agent Test Suite")
    print("=" * 70)

    tests = [
        test_agent_parse_status_query,
        test_agent_parse_ticket_key_query,
        test_agent_parse_search_query,
        test_agent_process_query_status,
        test_agent_process_query_ticket_details,
        test_agent_process_query_no_results,
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
        print("\n✓ All JIRA agent tests passed!")
        return 0
    else:
        print("\n✗ Some tests failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())
