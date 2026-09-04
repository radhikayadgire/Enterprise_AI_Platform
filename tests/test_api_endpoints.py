"""Integration tests for FastAPI JIRA endpoints."""

import sys
import os
from unittest.mock import Mock, patch
from fastapi.testclient import TestClient

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def test_health_endpoint():
    """Test the health check endpoint."""
    print("\nTesting GET /health endpoint...")

    try:
        from backend.main import app

        client = TestClient(app)
        response = client.get("/health")

        if response.status_code != 200:
            print(f"✗ Expected status 200, got {response.status_code}")
            return False

        data = response.json()
        if 'status' not in data:
            print(f"✗ Response missing 'status' field: {data}")
            return False

        if data['status'] != 'healthy':
            print(f"✗ Expected status 'healthy', got '{data['status']}'")
            return False

        # Verify initialization status fields are present
        if 'jira_tool_initialized' not in data or 'jira_agent_initialized' not in data:
            print(f"✗ Response missing initialization status fields: {data}")
            return False

        print(f"✓ Health endpoint returned: {data}")
        return True

    except Exception as e:
        print(f"✗ Health endpoint test failed: {e}")
        return False


def test_root_endpoint():
    """Test the root endpoint returns API information."""
    print("\nTesting GET / endpoint...")

    try:
        from backend.main import app

        client = TestClient(app)
        response = client.get("/")

        if response.status_code != 200:
            print(f"✗ Expected status 200, got {response.status_code}")
            return False

        data = response.json()

        # Verify required fields
        required_fields = ['message', 'version', 'endpoints']
        for field in required_fields:
            if field not in data:
                print(f"✗ Response missing field '{field}': {data}")
                return False

        # Verify endpoints list
        endpoints = data['endpoints']
        expected_endpoints = ['/jira/query', '/jira/status', '/jira/search', '/jira/jql']
        for endpoint in expected_endpoints:
            if endpoint not in endpoints:
                print(f"✗ Missing endpoint '{endpoint}' in response: {endpoints}")
                return False

        print(f"✓ Root endpoint returned API info with {len(endpoints)} endpoints")
        return True

    except Exception as e:
        print(f"✗ Root endpoint test failed: {e}")
        return False


def test_jira_query_endpoint():
    """Test POST /jira/query with natural language query."""
    print("\nTesting POST /jira/query endpoint...")

    try:
        from backend.main import app

        # Mock the JIRA agent
        with patch('backend.main.jira_agent') as mock_agent:
            mock_agent.process_query.return_value = "Found 3 ticket(s) with status 'In Progress'"

            client = TestClient(app)
            response = client.post(
                "/jira/query",
                json={"query": "Fetch tickets with status 'In Progress'", "max_results": 50}
            )

            if response.status_code != 200:
                print(f"✗ Expected status 200, got {response.status_code}: {response.json()}")
                return False

            data = response.json()

            # Verify response structure
            if 'query' not in data or 'response' not in data or 'status' not in data:
                print(f"✗ Response missing required fields: {data}")
                return False

            if data['query'] != "Fetch tickets with status 'In Progress'":
                print(f"✗ Query mismatch: {data['query']}")
                return False

            if data['status'] != 'success':
                print(f"✗ Expected status 'success', got '{data['status']}'")
                return False

            # Verify agent was called
            mock_agent.process_query.assert_called_once_with("Fetch tickets with status 'In Progress'")

            print("✓ JIRA query endpoint test passed")
            return True

    except Exception as e:
        print(f"✗ JIRA query endpoint test failed: {e}")
        return False


def test_jira_query_endpoint_no_agent():
    """Test POST /jira/query returns 503 when agent not initialized."""
    print("\nTesting POST /jira/query without initialized agent...")

    try:
        from backend.main import app

        with patch('backend.main.jira_agent', None):
            client = TestClient(app)
            response = client.post(
                "/jira/query",
                json={"query": "Test query"}
            )

            if response.status_code != 503:
                print(f"✗ Expected status 503, got {response.status_code}")
                return False

            data = response.json()
            if 'detail' not in data:
                print(f"✗ Error response missing 'detail': {data}")
                return False

            if 'not initialized' not in data['detail']:
                print(f"✗ Error message doesn't mention initialization: {data['detail']}")
                return False

            print("✓ Correctly returns 503 when agent not initialized")
            return True

    except Exception as e:
        print(f"✗ Query endpoint no-agent test failed: {e}")
        return False


def test_status_endpoint():
    """Test POST /jira/status endpoint."""
    print("\nTesting POST /jira/status endpoint...")

    try:
        from backend.main import app

        with patch('backend.main.jira_tool') as mock_tool:
            mock_tool.fetch_tickets_by_status.return_value = [
                {
                    'id': '1',
                    'key': 'TEST-1',
                    'summary': 'Test ticket',
                    'status': 'Done',
                    'assignee': 'John Doe'
                },
                {
                    'id': '2',
                    'key': 'TEST-2',
                    'summary': 'Another ticket',
                    'status': 'Done',
                    'assignee': 'Jane Smith'
                }
            ]

            client = TestClient(app)
            response = client.post(
                "/jira/status",
                json={"status": "Done", "max_results": 50}
            )

            if response.status_code != 200:
                print(f"✗ Expected status 200, got {response.status_code}")
                return False

            data = response.json()

            # Verify response structure
            if 'status' not in data or 'count' not in data or 'tickets' not in data:
                print(f"✗ Response missing required fields: {data.keys()}")
                return False

            if data['status'] != 'Done':
                print(f"✗ Status mismatch: {data['status']}")
                return False

            if data['count'] != 2:
                print(f"✗ Expected count 2, got {data['count']}")
                return False

            if len(data['tickets']) != 2:
                print(f"✗ Expected 2 tickets, got {len(data['tickets'])}")
                return False

            # Verify tool was called correctly
            mock_tool.fetch_tickets_by_status.assert_called_once_with(
                status='Done',
                max_results=50,
                project=None
            )

            print("✓ Status endpoint test passed")
            return True

    except Exception as e:
        print(f"✗ Status endpoint test failed: {e}")
        return False


def test_status_endpoint_with_project():
    """Test POST /jira/status with project filter."""
    print("\nTesting POST /jira/status with project filter...")

    try:
        from backend.main import app

        with patch('backend.main.jira_tool') as mock_tool:
            mock_tool.fetch_tickets_by_status.return_value = []

            client = TestClient(app)
            response = client.post(
                "/jira/status",
                json={"status": "In Progress", "project": "MYPROJ", "max_results": 20}
            )

            if response.status_code != 200:
                print(f"✗ Expected status 200, got {response.status_code}")
                return False

            # Verify tool was called with project parameter
            mock_tool.fetch_tickets_by_status.assert_called_once_with(
                status='In Progress',
                max_results=20,
                project='MYPROJ'
            )

            print("✓ Status endpoint with project test passed")
            return True

    except Exception as e:
        print(f"✗ Status endpoint with project test failed: {e}")
        return False


def test_ticket_details_endpoint():
    """Test GET /jira/ticket/{ticket_key} endpoint."""
    print("\nTesting GET /jira/ticket/{ticket_key} endpoint...")

    try:
        from backend.main import app

        with patch('backend.main.jira_tool') as mock_tool:
            mock_tool.get_ticket_details.return_value = {
                'id': '5001',
                'key': 'PROJ-999',
                'summary': 'Critical production bug',
                'description': 'System is down',
                'status': 'Critical',
                'assignee': 'Oncall Engineer',
                'reporter': 'Alert System',
                'priority': 'Highest',
                'created': '2026-09-04T08:00:00',
                'updated': '2026-09-04T08:15:00',
                'issue_type': 'Incident'
            }

            client = TestClient(app)
            response = client.get("/jira/ticket/PROJ-999")

            if response.status_code != 200:
                print(f"✗ Expected status 200, got {response.status_code}")
                return False

            data = response.json()

            # Verify all expected fields are present
            expected_fields = ['id', 'key', 'summary', 'description', 'status',
                             'assignee', 'reporter', 'priority', 'created', 'updated', 'issue_type']
            for field in expected_fields:
                if field not in data:
                    print(f"✗ Response missing field '{field}'")
                    return False

            if data['key'] != 'PROJ-999':
                print(f"✗ Wrong ticket key: {data['key']}")
                return False

            # Verify tool was called with correct key
            mock_tool.get_ticket_details.assert_called_once_with('PROJ-999')

            print("✓ Ticket details endpoint test passed")
            return True

    except Exception as e:
        print(f"✗ Ticket details endpoint test failed: {e}")
        return False


def test_ticket_details_not_found():
    """Test GET /jira/ticket/{ticket_key} with non-existent ticket."""
    print("\nTesting GET /jira/ticket/{ticket_key} with non-existent ticket...")

    try:
        from backend.main import app

        with patch('backend.main.jira_tool') as mock_tool:
            mock_tool.get_ticket_details.side_effect = Exception("Ticket NOTFOUND-1 not found")

            client = TestClient(app)
            response = client.get("/jira/ticket/NOTFOUND-1")

            if response.status_code != 404:
                print(f"✗ Expected status 404, got {response.status_code}")
                return False

            data = response.json()
            if 'detail' not in data:
                print(f"✗ Error response missing 'detail': {data}")
                return False

            print("✓ Correctly returns 404 for non-existent ticket")
            return True

    except Exception as e:
        print(f"✗ Ticket not found test failed: {e}")
        return False


def test_search_endpoint():
    """Test POST /jira/search endpoint."""
    print("\nTesting POST /jira/search endpoint...")

    try:
        from backend.main import app

        with patch('backend.main.jira_tool') as mock_tool:
            mock_tool.search_tickets.return_value = [
                {
                    'key': 'BUG-101',
                    'summary': 'Login authentication fails',
                    'status': 'Open'
                }
            ]

            client = TestClient(app)
            response = client.post(
                "/jira/search",
                json={"query": "authentication", "max_results": 30}
            )

            if response.status_code != 200:
                print(f"✗ Expected status 200, got {response.status_code}")
                return False

            data = response.json()

            if 'search_query' not in data or 'count' not in data or 'tickets' not in data:
                print(f"✗ Response missing required fields: {data.keys()}")
                return False

            if data['search_query'] != 'authentication':
                print(f"✗ Search query mismatch: {data['search_query']}")
                return False

            if data['count'] != 1:
                print(f"✗ Expected count 1, got {data['count']}")
                return False

            # Verify tool was called correctly
            mock_tool.search_tickets.assert_called_once_with(
                search_text='authentication',
                max_results=30
            )

            print("✓ Search endpoint test passed")
            return True

    except Exception as e:
        print(f"✗ Search endpoint test failed: {e}")
        return False


def test_jql_endpoint():
    """Test POST /jira/jql endpoint."""
    print("\nTesting POST /jira/jql endpoint...")

    try:
        from backend.main import app

        with patch('backend.main.jira_tool') as mock_tool:
            mock_tool.fetch_tickets_by_jql.return_value = [
                {
                    'key': 'URGENT-1',
                    'summary': 'Critical issue',
                    'status': 'In Progress',
                    'priority': 'Highest'
                },
                {
                    'key': 'URGENT-2',
                    'summary': 'Another critical issue',
                    'status': 'In Progress',
                    'priority': 'Highest'
                }
            ]

            client = TestClient(app)
            jql_query = 'priority = Highest AND status = "In Progress"'
            response = client.post(
                "/jira/jql",
                json={"jql": jql_query, "max_results": 100}
            )

            if response.status_code != 200:
                print(f"✗ Expected status 200, got {response.status_code}")
                return False

            data = response.json()

            if 'jql' not in data or 'count' not in data or 'tickets' not in data:
                print(f"✗ Response missing required fields: {data.keys()}")
                return False

            if data['jql'] != jql_query:
                print(f"✗ JQL mismatch: {data['jql']}")
                return False

            if data['count'] != 2:
                print(f"✗ Expected count 2, got {data['count']}")
                return False

            # Verify tool was called correctly
            mock_tool.fetch_tickets_by_jql.assert_called_once_with(
                jql_query=jql_query,
                max_results=100
            )

            print("✓ JQL endpoint test passed")
            return True

    except Exception as e:
        print(f"✗ JQL endpoint test failed: {e}")
        return False


def main():
    """Run all API endpoint tests."""
    print("=" * 70)
    print("API Endpoints Test Suite")
    print("=" * 70)

    tests = [
        test_health_endpoint,
        test_root_endpoint,
        test_jira_query_endpoint,
        test_jira_query_endpoint_no_agent,
        test_status_endpoint,
        test_status_endpoint_with_project,
        test_ticket_details_endpoint,
        test_ticket_details_not_found,
        test_search_endpoint,
        test_jql_endpoint,
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
        print("\n✓ All API endpoint tests passed!")
        return 0
    else:
        print("\n✗ Some tests failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())
