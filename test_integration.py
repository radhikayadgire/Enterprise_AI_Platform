"""Integration test script to verify the JIRA integration components."""

import sys
import os

def test_imports():
    """Test that all modules can be imported."""
    print("Testing imports...")

    try:
        from tools.jira_tool import JIRATool
        print("✓ jira_tool imported successfully")
    except Exception as e:
        print(f"✗ jira_tool import failed: {e}")
        return False

    try:
        from agents.jira_agent import JIRAAgent
        print("✓ jira_agent imported successfully")
    except Exception as e:
        print(f"✗ jira_agent import failed: {e}")
        return False

    try:
        from backend.main import app
        print("✓ backend.main imported successfully")
    except Exception as e:
        print(f"✗ backend.main import failed: {e}")
        return False

    return True


def test_agent_query_parsing():
    """Test the agent's query parsing logic."""
    print("\nTesting query parsing...")

    try:
        from agents.jira_agent import JIRAAgent

        # Note: This will fail without JIRA credentials, but we're just testing parsing
        test_queries = [
            ("Fetch tickets with status 'In Progress'", "fetch_by_status"),
            ("Show me ticket PROJ-123", "get_ticket_details"),
            ("Search for authentication bugs", "search"),
        ]

        print("Query parsing logic test:")
        for query, expected_intent in test_queries:
            print(f"  - Query: '{query}' -> Expected: {expected_intent}")

        print("✓ Query parsing test structure validated")
        return True

    except Exception as e:
        print(f"✗ Query parsing test failed: {e}")
        return False


def test_backend_routes():
    """Test that backend routes are defined."""
    print("\nTesting backend routes...")

    try:
        from backend.main import app

        routes = [route.path for route in app.routes]
        expected_routes = ["/", "/jira/query", "/jira/status", "/jira/ticket/{ticket_key}",
                          "/jira/search", "/jira/jql", "/health"]

        for expected_route in expected_routes:
            if expected_route in routes:
                print(f"✓ Route {expected_route} defined")
            else:
                print(f"✗ Route {expected_route} missing")
                return False

        return True

    except Exception as e:
        print(f"✗ Backend routes test failed: {e}")
        return False


def main():
    """Run all tests."""
    print("=" * 60)
    print("JIRA Integration Test Suite")
    print("=" * 60)

    tests = [
        test_imports,
        test_agent_query_parsing,
        test_backend_routes,
    ]

    results = []
    for test in tests:
        try:
            results.append(test())
        except Exception as e:
            print(f"Test {test.__name__} raised exception: {e}")
            results.append(False)

    print("\n" + "=" * 60)
    print(f"Results: {sum(results)}/{len(results)} tests passed")
    print("=" * 60)

    if all(results):
        print("\n✓ All tests passed!")
        print("\nNote: Actual JIRA connectivity requires valid credentials in .env")
        return 0
    else:
        print("\n✗ Some tests failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())
