"""Streamlit UI for Enterprise AI Platform JIRA Integration."""

import streamlit as st
import requests
import json
from typing import Dict, Any, List

# Configuration
BACKEND_URL = "http://localhost:8000"

st.set_page_config(
    page_title="Enterprise AI Platform - JIRA Integration",
    page_icon="🎫",
    layout="wide"
)

# Custom CSS
st.markdown("""
<style>
    .ticket-card {
        background-color: #f0f2f6;
        padding: 15px;
        border-radius: 5px;
        margin: 10px 0;
    }
    .ticket-key {
        font-weight: bold;
        color: #0066cc;
        font-size: 1.1em;
    }
    .status-badge {
        padding: 5px 10px;
        border-radius: 3px;
        font-size: 0.9em;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)


def check_backend_health() -> bool:
    """Check if backend is running."""
    try:
        response = requests.get(f"{BACKEND_URL}/health", timeout=2)
        return response.status_code == 200
    except:
        return False


def display_ticket(ticket: Dict[str, Any]):
    """Display a JIRA ticket in a formatted card."""
    with st.container():
        st.markdown(f"""
        <div class="ticket-card">
            <span class="ticket-key">{ticket.get('key', 'N/A')}</span>
            <p><strong>Summary:</strong> {ticket.get('summary', 'N/A')}</p>
            <p><strong>Status:</strong> {ticket.get('status', 'N/A')}</p>
            <p><strong>Assignee:</strong> {ticket.get('assignee', 'Unassigned')}</p>
            <p><strong>Description:</strong> {ticket.get('description', 'No description')[:200]}...</p>
        </div>
        """, unsafe_allow_html=True)


def main():
    """Main Streamlit application."""

    st.title("🎫 Enterprise AI Platform - JIRA Integration")
    st.markdown("---")

    # Check backend health
    if not check_backend_health():
        st.error("⚠️ Backend service is not running. Please start the backend server first.")
        st.info("Run: `python backend/main.py` or `uvicorn backend.main:app --reload`")
        return

    # Sidebar for navigation
    st.sidebar.title("Navigation")
    page = st.sidebar.radio(
        "Select Query Type",
        ["Natural Language Query", "Status-Based Search", "Ticket Details", "JQL Query", "Text Search"]
    )

    st.sidebar.markdown("---")
    st.sidebar.info("""
    **Quick Examples:**
    - "Fetch all tickets with status 'in progress'"
    - "Show me high priority bugs"
    - "What tickets are currently blocked?"
    """)

    # Main content area
    if page == "Natural Language Query":
        st.header("🤖 Natural Language JIRA Query")
        st.write("Ask questions about JIRA tickets in plain English using AI.")

        query = st.text_input(
            "Enter your query:",
            placeholder="Fetch the descriptions and IDs of all tickets with status 'in progress'"
        )

        if st.button("Submit Query"):
            if query:
                with st.spinner("Processing your query..."):
                    try:
                        response = requests.post(
                            f"{BACKEND_URL}/jira/query",
                            json={"query": query, "max_results": 50}
                        )

                        if response.status_code == 200:
                            result = response.json()
                            st.success("Query processed successfully!")
                            st.markdown("### Response:")
                            st.write(result.get("response", "No response"))
                        else:
                            st.error(f"Error: {response.json().get('detail', 'Unknown error')}")
                    except Exception as e:
                        st.error(f"Connection error: {str(e)}")
            else:
                st.warning("Please enter a query.")

    elif page == "Status-Based Search":
        st.header("📊 Fetch Tickets by Status")

        col1, col2 = st.columns(2)

        with col1:
            status = st.text_input(
                "Status:",
                placeholder="In Progress, Done, To Do, etc."
            )

        with col2:
            project = st.text_input(
                "Project Key (optional):",
                placeholder="PROJ, ENG, etc."
            )

        max_results = st.slider("Maximum results:", 10, 100, 50)

        if st.button("Fetch Tickets"):
            if status:
                with st.spinner(f"Fetching tickets with status '{status}'..."):
                    try:
                        payload = {
                            "status": status,
                            "max_results": max_results
                        }
                        if project:
                            payload["project"] = project

                        response = requests.post(
                            f"{BACKEND_URL}/jira/status",
                            json=payload
                        )

                        if response.status_code == 200:
                            result = response.json()
                            st.success(f"Found {result.get('count', 0)} ticket(s)")

                            if result.get('tickets'):
                                for ticket in result['tickets']:
                                    display_ticket(ticket)
                            else:
                                st.info("No tickets found with the specified criteria.")
                        else:
                            st.error(f"Error: {response.json().get('detail', 'Unknown error')}")
                    except Exception as e:
                        st.error(f"Connection error: {str(e)}")
            else:
                st.warning("Please enter a status.")

    elif page == "Ticket Details":
        st.header("🔍 Get Ticket Details")

        ticket_key = st.text_input(
            "Ticket Key:",
            placeholder="PROJ-123"
        )

        if st.button("Get Details"):
            if ticket_key:
                with st.spinner(f"Fetching details for {ticket_key}..."):
                    try:
                        response = requests.get(
                            f"{BACKEND_URL}/jira/ticket/{ticket_key}"
                        )

                        if response.status_code == 200:
                            ticket = response.json()
                            st.success(f"Ticket found: {ticket['key']}")

                            # Display detailed information
                            col1, col2 = st.columns(2)

                            with col1:
                                st.markdown("### Basic Information")
                                st.write(f"**Key:** {ticket.get('key')}")
                                st.write(f"**Summary:** {ticket.get('summary')}")
                                st.write(f"**Status:** {ticket.get('status')}")
                                st.write(f"**Type:** {ticket.get('issue_type', 'N/A')}")

                            with col2:
                                st.markdown("### Assignment & Dates")
                                st.write(f"**Assignee:** {ticket.get('assignee')}")
                                st.write(f"**Reporter:** {ticket.get('reporter', 'N/A')}")
                                st.write(f"**Priority:** {ticket.get('priority', 'N/A')}")
                                st.write(f"**Created:** {ticket.get('created', 'N/A')[:10]}")
                                st.write(f"**Updated:** {ticket.get('updated', 'N/A')[:10]}")

                            st.markdown("### Description")
                            st.write(ticket.get('description', 'No description'))
                        else:
                            st.error(f"Error: {response.json().get('detail', 'Ticket not found')}")
                    except Exception as e:
                        st.error(f"Connection error: {str(e)}")
            else:
                st.warning("Please enter a ticket key.")

    elif page == "JQL Query":
        st.header("⚡ Execute JQL Query")
        st.write("Run custom JIRA Query Language (JQL) queries.")

        jql = st.text_area(
            "JQL Query:",
            placeholder='project = PROJ AND status = "In Progress"',
            height=100
        )

        max_results = st.slider("Maximum results:", 10, 100, 50)

        st.markdown("**JQL Examples:**")
        st.code('status = "In Progress" AND assignee = currentUser()')
        st.code('project = PROJ AND priority = High')
        st.code('created >= -7d ORDER BY created DESC')

        if st.button("Execute Query"):
            if jql:
                with st.spinner("Executing JQL query..."):
                    try:
                        response = requests.post(
                            f"{BACKEND_URL}/jira/jql",
                            json={"jql": jql, "max_results": max_results}
                        )

                        if response.status_code == 200:
                            result = response.json()
                            st.success(f"Found {result.get('count', 0)} ticket(s)")

                            if result.get('tickets'):
                                for ticket in result['tickets']:
                                    display_ticket(ticket)
                            else:
                                st.info("No tickets found matching the JQL query.")
                        else:
                            st.error(f"Error: {response.json().get('detail', 'Unknown error')}")
                    except Exception as e:
                        st.error(f"Connection error: {str(e)}")
            else:
                st.warning("Please enter a JQL query.")

    elif page == "Text Search":
        st.header("🔎 Search Tickets")
        st.write("Search for tickets containing specific text in summary or description.")

        search_text = st.text_input(
            "Search Text:",
            placeholder="bug, feature, authentication, etc."
        )

        max_results = st.slider("Maximum results:", 10, 100, 50)

        if st.button("Search"):
            if search_text:
                with st.spinner(f"Searching for '{search_text}'..."):
                    try:
                        response = requests.post(
                            f"{BACKEND_URL}/jira/search",
                            json={"query": search_text, "max_results": max_results}
                        )

                        if response.status_code == 200:
                            result = response.json()
                            st.success(f"Found {result.get('count', 0)} ticket(s)")

                            if result.get('tickets'):
                                for ticket in result['tickets']:
                                    display_ticket(ticket)
                            else:
                                st.info("No tickets found matching the search criteria.")
                        else:
                            st.error(f"Error: {response.json().get('detail', 'Unknown error')}")
                    except Exception as e:
                        st.error(f"Connection error: {str(e)}")
            else:
                st.warning("Please enter search text.")


if __name__ == "__main__":
    main()
