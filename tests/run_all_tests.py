"""Master test runner for all JIRA integration tests."""

import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def main():
    """Run all test suites."""
    print("=" * 80)
    print("JIRA Integration - Complete Test Suite")
    print("=" * 80)
    print("\nRunning comprehensive tests for JIRA integration features:")
    print("  - JIRA Agent (query parsing and processing)")
    print("  - JIRA Tool (API integration methods)")
    print("  - Backend API Endpoints (FastAPI routes)")
    print("\n" + "=" * 80)

    # Import test modules
    try:
        from tests import test_jira_agent, test_jira_tool, test_api_endpoints
    except ImportError:
        print("\n✗ Failed to import test modules")
        print("Make sure you're running from the project root directory")
        return 1

    test_suites = [
        ("JIRA Agent Tests", test_jira_agent.main),
        ("JIRA Tool Tests", test_jira_tool.main),
        ("API Endpoints Tests", test_api_endpoints.main),
    ]

    suite_results = []

    for suite_name, suite_main in test_suites:
        print(f"\n{'=' * 80}")
        print(f"Running: {suite_name}")
        print('=' * 80)

        result = suite_main()
        suite_results.append((suite_name, result == 0))

    # Print overall summary
    print("\n" + "=" * 80)
    print("OVERALL TEST SUMMARY")
    print("=" * 80)

    for suite_name, passed in suite_results:
        status = "✓ PASSED" if passed else "✗ FAILED"
        print(f"{status:>12} - {suite_name}")

    print("=" * 80)

    total_passed = sum(1 for _, passed in suite_results if passed)
    total_suites = len(suite_results)

    print(f"\nTest Suites: {total_passed}/{total_suites} passed")

    if all(passed for _, passed in suite_results):
        print("\n🎉 All test suites passed!")
        print("\nNote: These tests use mocks and don't require JIRA credentials.")
        print("For end-to-end testing with real JIRA, configure .env and run manual tests.")
        return 0
    else:
        print("\n⚠️  Some test suites failed. Review the output above for details.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
