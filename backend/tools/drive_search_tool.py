"""
Custom LangChain tool for searching Google Drive files.

This tool is bound to the Gemini LLM via LangChain's tool calling
interface. The LLM generates the Google Drive API q parameter string,
and this tool executes the actual search.
"""

import json
from typing import Optional

from langchain_core.tools import tool

from backend.utils.logger import get_logger

logger = get_logger(__name__)

# Global reference to the Drive service instance.
# Set by agent_service.py during initialization.
_drive_service = None


def set_drive_service(service) -> None:
    """
    Set the DriveService instance for the tool to use.
    
    Called once during app startup by agent_service.py.
    This pattern avoids circular imports and allows the tool
    to be defined with the @tool decorator while still having
    access to the Drive service.
    """
    global _drive_service
    _drive_service = service
    logger.info("DriveSearchTool connected to Drive service")


@tool
def search_drive_files(query: str) -> str:
    """Search Google Drive files using a Google Drive API q parameter query string.
    
    Use this tool to search for files in Google Drive. The input must be a valid
    Google Drive API q parameter query string.
    
    IMPORTANT QUERY SYNTAX RULES:
    - Use single quotes for string values: name contains 'report'
    - Combine conditions with 'and' or 'or'
    - Available operators: =, !=, contains, >, <, >=, <=
    - Date format must be RFC 3339: '2026-01-01T00:00:00Z'
    
    QUERY EXAMPLES:
    - name contains 'finance' and mimeType='application/pdf'
    - modifiedTime > '2026-05-01T00:00:00Z' and name contains 'report'  
    - fullText contains 'invoice'
    - mimeType='application/vnd.google-apps.spreadsheet'
    - name contains 'logo' and (mimeType='image/png' or mimeType='image/jpeg')
    - mimeType='application/vnd.google-apps.document' and modifiedTime > '2026-05-01T00:00:00Z'
    
    Args:
        query: A valid Google Drive API q parameter query string.
    
    Returns:
        JSON string containing the search results with file metadata,
        or an error message if the search fails.
    """
    logger.info(f"DriveSearchTool called with query: {query}")

    if _drive_service is None:
        error_msg = "Drive service not initialized. Check your service account configuration."
        logger.error(error_msg)
        return json.dumps({"error": error_msg, "files": []})

    try:
        # Execute the search via the Drive service
        results = _drive_service.search_files(query=query, page_size=20)

        files = results.get("files", [])
        total = results.get("total_count", 0)

        logger.info(f"DriveSearchTool found {total} file(s)")

        # Format results for the LLM to interpret
        if not files:
            return json.dumps({
                "message": "No files found matching the query.",
                "files": [],
                "total_count": 0,
                "query_used": results.get("query_used", query),
            })

        # Build a clean file list for the LLM response
        file_list = []
        for f in files:
            file_list.append({
                "id": f.get("id", ""),
                "name": f.get("name", "Unknown"),
                "mimeType": f.get("mimeType", ""),
                "modifiedTime": f.get("modifiedTime", ""),
                "webViewLink": f.get("webViewLink", ""),
                "iconLink": f.get("iconLink", ""),
                "size": f.get("size", ""),
                "thumbnailLink": f.get("thumbnailLink", ""),
            })

        return json.dumps({
            "message": f"Found {total} file(s) matching your query.",
            "files": file_list,
            "total_count": total,
            "query_used": results.get("query_used", query),
        })

    except ValueError as e:
        # Invalid query syntax
        error_msg = f"Invalid query: {str(e)}"
        logger.warning(error_msg)
        return json.dumps({"error": error_msg, "files": []})

    except Exception as e:
        # Unexpected errors
        error_msg = f"Search failed: {str(e)}"
        logger.error(error_msg)
        return json.dumps({"error": error_msg, "files": []})
