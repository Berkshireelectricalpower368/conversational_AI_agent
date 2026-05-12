"""
Chat UI components for the Streamlit frontend.

Provides the welcome screen, message rendering, typing indicator,
and query suggestion chips.
"""

import streamlit as st
from typing import Dict, List, Optional
from frontend.components.file_card import render_file_results


# ── Example queries for the welcome screen ───────────────────
EXAMPLE_QUERIES = [
    "🔍 Find finance PDFs from last week",
    "🖼️ Show all images related to logo",
    "📄 Find documents containing invoice",
    "📊 Show spreadsheets uploaded this month",
    "📝 Find files named project report",
    "🔐 Search files related to cybersecurity",
]


def render_welcome() -> None:
    """
    Render the welcome screen shown when the chat is empty.
    
    Displays app branding, description, and clickable example queries.
    """
    st.markdown(
        """
        <div class="welcome-container">
            <div class="welcome-icon">🗂️</div>
            <h1 class="welcome-title">Drive Discovery Assistant</h1>
            <p class="welcome-subtitle">
                Search your Google Drive using natural language. 
                Ask me anything about your files!
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Example query chips
    st.markdown(
        '<div class="chips-label">Try asking:</div>',
        unsafe_allow_html=True,
    )

    # Create 2 columns of 3 chips each
    cols = st.columns(2)
    for i, query in enumerate(EXAMPLE_QUERIES):
        col = cols[i % 2]
        with col:
            # Use a button for each example query
            if st.button(
                query,
                key=f"example_{i}",
                use_container_width=True,
            ):
                # Set the query in session state so the main app can process it
                st.session_state["pending_query"] = query.split(" ", 1)[1] if " " in query else query


def render_message(role: str, content: str, files: Optional[List[Dict]] = None) -> None:
    """
    Render a single chat message with optional file results.
    
    Args:
        role: 'user' or 'assistant'
        content: Message text content
        files: Optional list of file results to display below the message
    """
    avatar = "👤" if role == "user" else "🤖"

    with st.chat_message(role, avatar=avatar):
        st.markdown(content)

        # Render file cards if present
        if files:
            render_file_results(files)


def render_chat_history(messages: List[Dict]) -> None:
    """
    Render all messages in the chat history.
    
    Args:
        messages: List of message dicts with 'role', 'content', and optional 'files'
    """
    for msg in messages:
        render_message(
            role=msg["role"],
            content=msg["content"],
            files=msg.get("files"),
        )


def render_typing_indicator() -> None:
    """
    Render a typing indicator while the AI is processing.
    
    Shows animated dots in an assistant message bubble.
    """
    st.markdown(
        """
        <div class="typing-indicator">
            <div class="typing-avatar">🤖</div>
            <div class="typing-dots">
                <span class="dot"></span>
                <span class="dot"></span>
                <span class="dot"></span>
            </div>
            <span class="typing-text">Searching your Drive...</span>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_query_badge(query_used: Optional[str]) -> None:
    """
    Display the generated Drive API query in a subtle badge.
    
    Useful for debugging and showing users what query was generated.
    """
    if query_used:
        with st.expander("🔧 Generated Drive Query", expanded=False):
            st.code(query_used, language="sql")
