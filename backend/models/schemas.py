"""
Pydantic schemas for API request/response models.

These models define the contract between the frontend and backend,
ensuring type safety and automatic validation.
"""

from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field


# ── Request Models ───────────────────────────────────────────

class ChatRequest(BaseModel):
    """
    Incoming chat request from the frontend.
    
    Attributes:
        query: The user's natural language search query.
        session_id: Unique session identifier for conversation memory.
    """
    query: str = Field(
        ...,
        min_length=1,
        max_length=1000,
        description="Natural language search query from the user",
        examples=["Find finance PDFs from last week"]
    )
    session_id: str = Field(
        ...,
        min_length=1,
        description="Session ID for tracking conversation history",
        examples=["session_abc123"]
    )


# ── Response Models ──────────────────────────────────────────

class FileResult(BaseModel):
    """
    A single file result from Google Drive search.
    
    Contains all the metadata needed to display a rich file card
    in the frontend UI.
    """
    id: str = Field(description="Google Drive file ID")
    name: str = Field(description="File name")
    mime_type: str = Field(description="MIME type of the file")
    modified_time: Optional[str] = Field(
        default=None,
        description="Last modified time in ISO 8601 format"
    )
    web_view_link: Optional[str] = Field(
        default=None,
        description="URL to view the file in Google Drive"
    )
    icon_link: Optional[str] = Field(
        default=None,
        description="URL of the file's icon"
    )
    size: Optional[str] = Field(
        default=None,
        description="File size in bytes (not available for Google Workspace files)"
    )
    thumbnail_link: Optional[str] = Field(
        default=None,
        description="URL of the file's thumbnail (if available)"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "id": "1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgVE2upms",
                "name": "Q4 Finance Report.pdf",
                "mime_type": "application/pdf",
                "modified_time": "2026-05-10T14:30:00.000Z",
                "web_view_link": "https://drive.google.com/file/d/1BxiMVs.../view",
                "icon_link": "https://drive-thirdparty.googleusercontent.com/16/type/application/pdf",
                "size": "2048576",
                "thumbnail_link": None,
            }
        }


class ChatResponse(BaseModel):
    """
    Response from the chat endpoint.
    
    Contains the AI's natural language response and any matching files.
    """
    message: str = Field(description="AI-generated response message")
    files: List[FileResult] = Field(
        default_factory=list,
        description="List of matching files from Google Drive"
    )
    query_used: Optional[str] = Field(
        default=None,
        description="The Google Drive API q parameter that was generated"
    )
    session_id: str = Field(description="Session ID for this conversation")


class SearchHistoryItem(BaseModel):
    """A single entry in the search history sidebar."""
    query: str = Field(description="The original user query")
    timestamp: str = Field(description="When the search was performed")
    result_count: int = Field(description="Number of files found")


class SearchHistoryResponse(BaseModel):
    """Response for the search history endpoint."""
    history: List[SearchHistoryItem] = Field(default_factory=list)
    session_id: str


class ErrorResponse(BaseModel):
    """Standardized error response format."""
    error: str = Field(description="Error message")
    detail: Optional[str] = Field(default=None, description="Additional error details")
