"""
API client for communicating with the FastAPI backend.

Provides simple functions to send chat messages and retrieve
search history from the backend server.
"""

import os
import requests
from typing import Any, Dict, Optional

# Backend URL — configurable via environment variable
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")

# Request timeout in seconds
TIMEOUT = 60


def send_message(query: str, session_id: str) -> Dict[str, Any]:
    """
    Send a chat message to the backend API.
    
    Args:
        query: Natural language search query.
        session_id: Session identifier for conversation memory.
    
    Returns:
        Dict with 'message', 'files', 'query_used', 'session_id'.
    
    Raises:
        ConnectionError: If the backend is not reachable.
        Exception: For other API errors.
    """
    url = f"{BACKEND_URL}/api/chat"

    try:
        response = requests.post(
            url,
            json={"query": query, "session_id": session_id},
            timeout=TIMEOUT,
            headers={"Content-Type": "application/json"},
        )

        if response.status_code == 200:
            return response.json()

        elif response.status_code == 503:
            return {
                "message": (
                    "⚠️ The AI agent is not initialized. "
                    "Please check the backend server configuration and logs."
                ),
                "files": [],
                "query_used": None,
                "session_id": session_id,
            }

        else:
            error_detail = ""
            try:
                error_data = response.json()
                error_detail = error_data.get("detail", error_data.get("error", ""))
            except Exception:
                error_detail = response.text[:200]

            return {
                "message": f"⚠️ Server error ({response.status_code}): {error_detail}",
                "files": [],
                "query_used": None,
                "session_id": session_id,
            }

    except requests.ConnectionError:
        return {
            "message": (
                "❌ Cannot connect to the backend server. "
                f"Make sure it's running at **{BACKEND_URL}**.\n\n"
                "Start the backend with:\n"
                "```\nuvicorn backend.main:app --reload\n```"
            ),
            "files": [],
            "query_used": None,
            "session_id": session_id,
        }

    except requests.Timeout:
        return {
            "message": (
                "⏱️ The request timed out. The search might be taking too long. "
                "Please try a simpler query."
            ),
            "files": [],
            "query_used": None,
            "session_id": session_id,
        }

    except Exception as e:
        return {
            "message": f"❌ Unexpected error: {str(e)}",
            "files": [],
            "query_used": None,
            "session_id": session_id,
        }


def get_search_history(session_id: str) -> list:
    """
    Retrieve search history from the backend.
    
    Args:
        session_id: Session identifier.
    
    Returns:
        List of search history items.
    """
    url = f"{BACKEND_URL}/api/history/{session_id}"

    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            return data.get("history", [])
    except Exception:
        pass

    return []


def clear_session(session_id: str) -> bool:
    """
    Clear a session's memory and history on the backend.
    
    Args:
        session_id: Session identifier.
    
    Returns:
        True if successful, False otherwise.
    """
    url = f"{BACKEND_URL}/api/session/{session_id}"

    try:
        response = requests.delete(url, timeout=10)
        return response.status_code == 200
    except Exception:
        return False


def check_backend_health() -> bool:
    """
    Check if the backend server is healthy.
    
    Returns:
        True if the backend is reachable and healthy.
    """
    url = f"{BACKEND_URL}/health"

    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            data = response.json()
            return data.get("status") == "healthy"
    except Exception:
        pass

    return False
