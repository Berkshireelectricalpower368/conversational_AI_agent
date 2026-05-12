"""
Streamlit frontend for the Google Drive File Discovery Assistant.

A modern conversational chat interface that lets users search
Google Drive files using natural language. Features include:
- Chat bubbles with user/assistant avatars
- File result cards with icons and Drive links
- Search history sidebar
- Loading animations
- Welcome screen with example queries

Run with: streamlit run frontend/app.py
"""

import uuid
import os
import sys

# ── Ensure project root is on sys.path ───────────────────────
# This allows `from frontend.x` and `from backend.x` imports to work
# without needing to manually set PYTHONPATH.
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

import streamlit as st

# ── Page Configuration (must be first Streamlit call) ────────
st.set_page_config(
    page_title="Drive Discovery Assistant",
    page_icon="🗂️",
    layout="centered",
    initial_sidebar_state="expanded",
    menu_items={
        "Get help": "https://github.com",
        "About": "AI-powered Google Drive File Discovery Assistant",
    },
)

# ── Load Custom CSS ──────────────────────────────────────────
css_path = os.path.join(os.path.dirname(__file__), "styles", "custom.css")
if os.path.exists(css_path):
    with open(css_path) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# ── Import Components (after page config) ────────────────────
from frontend.components.chat_ui import (
    render_welcome,
    render_chat_history,
    render_message,
    render_query_badge,
)
from frontend.components.sidebar import render_sidebar
from frontend.utils.api_client import send_message, get_search_history


# ── Session State Initialization ─────────────────────────────
if "session_id" not in st.session_state:
    st.session_state["session_id"] = str(uuid.uuid4())

if "messages" not in st.session_state:
    st.session_state["messages"] = []

if "pending_query" not in st.session_state:
    st.session_state["pending_query"] = None


def process_query(query: str) -> None:
    """
    Process a user query: send to backend and display results.
    
    This function:
    1. Adds the user message to chat history
    2. Shows a loading spinner
    3. Sends the query to the FastAPI backend
    4. Displays the AI response and file results
    """
    session_id = st.session_state["session_id"]

    # Add user message to history
    st.session_state["messages"].append({
        "role": "user",
        "content": query,
        "files": None,
    })

    # Display user message immediately
    render_message("user", query)

    # Show loading state and send to backend
    with st.chat_message("assistant", avatar="🤖"):
        with st.spinner("🔍 Searching your Drive..."):
            response = send_message(query, session_id)

    # Extract response data
    ai_message = response.get("message", "I couldn't process that query. Please try again.")
    files = response.get("files", [])
    query_used = response.get("query_used")

    # Convert file objects to dicts if needed
    file_dicts = []
    for f in files:
        if isinstance(f, dict):
            file_dicts.append(f)
        else:
            file_dicts.append(f.dict() if hasattr(f, "dict") else vars(f))

    # Add assistant response to history
    st.session_state["messages"].append({
        "role": "assistant",
        "content": ai_message,
        "files": file_dicts if file_dicts else None,
        "query_used": query_used,
    })

    # Rerun to display the response in the chat history
    st.rerun()


# ── Main App Logic ───────────────────────────────────────────

def main():
    """Main application entry point."""

    session_id = st.session_state["session_id"]

    # ── Render Sidebar ───────────────────────────────────────
    search_history = get_search_history(session_id)
    render_sidebar(session_id, search_history)

    # ── Main Content Area ────────────────────────────────────

    # Show welcome screen if no messages yet
    if not st.session_state["messages"]:
        render_welcome()

    # Render existing chat history
    render_chat_history(st.session_state["messages"])

    # Show query details for the last assistant message
    if st.session_state["messages"]:
        last_msg = st.session_state["messages"][-1]
        if last_msg["role"] == "assistant" and last_msg.get("query_used"):
            render_query_badge(last_msg["query_used"])

    # ── Handle Pending Query (from example chips / history) ──
    if st.session_state.get("pending_query"):
        query = st.session_state["pending_query"]
        st.session_state["pending_query"] = None
        process_query(query)

    # ── Chat Input ───────────────────────────────────────────
    if prompt := st.chat_input(
        "Ask me to find files... (e.g., 'Find PDFs from last week')",
    ):
        process_query(prompt)


# Run the app
main()
