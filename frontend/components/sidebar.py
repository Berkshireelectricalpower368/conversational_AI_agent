"""
Sidebar component for the Streamlit frontend.

Provides:
- App branding
- New Chat button
- Search history
- Backend status indicator
- About section
"""

import streamlit as st
from typing import List, Dict
from frontend.utils.api_client import check_backend_health


def render_sidebar(session_id: str, search_history: List[Dict]) -> None:
    """
    Render the sidebar with branding, controls, and search history.
    
    Args:
        session_id: Current session ID
        search_history: List of past search items
    """
    with st.sidebar:
        # ── App Branding ─────────────────────────────────────
        st.markdown(
            """
            <div class="sidebar-brand">
                <div class="sidebar-logo">🗂️</div>
                <div class="sidebar-title">Drive Discovery</div>
                <div class="sidebar-subtitle">AI-Powered File Search</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.divider()

        # ── New Chat Button ──────────────────────────────────
        if st.button("✨ New Chat", use_container_width=True, type="primary"):
            # Clear chat history in session state
            st.session_state["messages"] = []
            st.session_state["pending_query"] = None
            # Clear backend session memory
            from frontend.utils.api_client import clear_session
            clear_session(session_id)
            # Generate new session ID
            import uuid
            st.session_state["session_id"] = str(uuid.uuid4())
            st.rerun()

        st.divider()

        # ── Search History ───────────────────────────────────
        st.markdown(
            '<div class="sidebar-section-title">📜 Recent Searches</div>',
            unsafe_allow_html=True,
        )

        if search_history:
            for i, item in enumerate(reversed(search_history[-10:])):
                query = item.get("query", "")
                count = item.get("result_count", 0)
                
                # Truncate long queries
                display_query = query[:40] + "..." if len(query) > 40 else query
                
                if st.button(
                    f"🔍 {display_query} ({count})",
                    key=f"history_{i}",
                    use_container_width=True,
                ):
                    st.session_state["pending_query"] = query
                    st.rerun()
        else:
            st.markdown(
                '<div class="sidebar-empty">No searches yet. Start by asking a question!</div>',
                unsafe_allow_html=True,
            )

        st.divider()

        # ── Backend Status ───────────────────────────────────
        st.markdown(
            '<div class="sidebar-section-title">⚡ Status</div>',
            unsafe_allow_html=True,
        )

        is_healthy = check_backend_health()
        if is_healthy:
            st.markdown(
                '<div class="status-badge status-online">● Backend Online</div>',
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                '<div class="status-badge status-offline">● Backend Offline</div>',
                unsafe_allow_html=True,
            )

        # ── About Section ────────────────────────────────────
        st.divider()

        st.markdown(
            """
            <div class="sidebar-about">
                <div class="sidebar-section-title">ℹ️ About</div>
                <p>An AI-powered assistant that helps you search and discover files in Google Drive using natural language.</p>
                <p class="sidebar-tech">
                    Built with <strong>FastAPI</strong> · <strong>LangChain</strong> · <strong>Gemini</strong> · <strong>Streamlit</strong>
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )
