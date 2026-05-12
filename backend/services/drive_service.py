"""
Google Drive API v3 service wrapper.

Handles authentication via Service Account and provides methods
to search files using the Drive API's files.list endpoint with
the q parameter for filtering.
"""

import json
import os
import time
from typing import Any, Dict, List, Optional

from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from backend.utils.logger import get_logger

logger = get_logger(__name__)

# Scopes required for read-only Drive access
SCOPES = ["https://www.googleapis.com/auth/drive.readonly"]


class DriveService:
    """
    Wrapper around Google Drive API v3 for file search operations.
    
    Authenticates using a Service Account and provides methods to
    search files with complex query parameters.
    """

    def __init__(self, service_account_source: str, folder_id: Optional[str] = None):
        """
        Initialize the Drive service.
        
        Args:
            service_account_source: Either a file path to the service account
                JSON key file, or the JSON string itself (for cloud deployment).
            folder_id: Optional folder ID to restrict searches to.
        """
        self.folder_id = folder_id
        self.service = self._authenticate(service_account_source)
        logger.info("Google Drive service initialized successfully")
        if folder_id:
            logger.info(f"Search scope: folder {folder_id}")
        else:
            logger.info("Search scope: all accessible files")

    def _authenticate(self, source: str):
        """
        Authenticate with Google Drive API using Service Account credentials.
        
        Supports both file path and JSON string inputs, making it flexible
        for both local development and cloud deployment.
        """
        try:
            # Check if source is a file path
            if os.path.isfile(source):
                logger.info(f"Authenticating with service account file: {source}")
                credentials = service_account.Credentials.from_service_account_file(
                    source, scopes=SCOPES
                )
            else:
                # Treat as JSON string (for cloud deployment via env vars)
                logger.info("Authenticating with service account JSON string")
                service_account_info = json.loads(source)
                credentials = service_account.Credentials.from_service_account_info(
                    service_account_info, scopes=SCOPES
                )

            # Build the Drive API service
            service = build("drive", "v3", credentials=credentials)
            logger.info("Drive API authentication successful")
            return service

        except json.JSONDecodeError as e:
            logger.error(f"Invalid service account JSON: {e}")
            raise ValueError(
                "GOOGLE_SERVICE_ACCOUNT_FILE must be a valid file path "
                "or a valid JSON string"
            ) from e
        except Exception as e:
            logger.error(f"Drive API authentication failed: {e}")
            raise

    def search_files(
        self,
        query: str,
        page_size: int = 20,
        order_by: str = "modifiedTime desc",
    ) -> Dict[str, Any]:
        """
        Search files in Google Drive using the q parameter.
        
        This is the core method that executes the AI-generated query
        against the Drive API's files.list endpoint.
        
        Args:
            query: Google Drive API q parameter string.
                   Example: "name contains 'finance' and mimeType='application/pdf'"
            page_size: Maximum number of results to return (1-100).
            order_by: Sort order for results.
        
        Returns:
            Dict with 'files' list and metadata.
        
        Raises:
            HttpError: If the Drive API returns an error.
            ValueError: If the query is invalid.
        """
        if not query or not query.strip():
            raise ValueError("Search query cannot be empty")

        # Build the complete query string
        full_query = self._build_query(query)
        logger.info(f"Executing Drive search: q='{full_query}'")

        # Fields to request from the API — only what we need
        fields = (
            "files(id, name, mimeType, modifiedTime, webViewLink, "
            "iconLink, size, thumbnailLink, parents)"
        )

        try:
            # Execute the search with retry logic for rate limits
            results = self._execute_with_retry(
                full_query, fields, page_size, order_by
            )

            files = results.get("files", [])
            logger.info(f"Search returned {len(files)} file(s)")

            # Deduplicate results by file ID
            seen_ids = set()
            unique_files = []
            for f in files:
                if f["id"] not in seen_ids:
                    seen_ids.add(f["id"])
                    unique_files.append(f)

            return {
                "files": unique_files,
                "total_count": len(unique_files),
                "query_used": full_query,
            }

        except HttpError as e:
            logger.error(f"Drive API error: {e}")
            if e.resp.status == 400:
                raise ValueError(
                    f"Invalid Drive query syntax: {query}. "
                    f"Error: {e.reason}"
                ) from e
            raise
        except Exception as e:
            logger.error(f"Unexpected search error: {e}")
            raise

    def _build_query(self, query: str) -> str:
        """
        Build the complete query string by appending standard filters.
        
        Always adds `trashed = false` and optionally scopes to a folder.
        """
        parts = [query.strip()]

        # Always exclude trashed files (unless already specified)
        if "trashed" not in query.lower():
            parts.append("trashed = false")

        # Scope to folder if configured
        if self.folder_id and "in parents" not in query.lower():
            parts.append(f"'{self.folder_id}' in parents")

        return " and ".join(parts)

    def _execute_with_retry(
        self,
        query: str,
        fields: str,
        page_size: int,
        order_by: str,
        max_retries: int = 3,
    ) -> Dict:
        """
        Execute the Drive API call with exponential backoff retry.
        
        Handles rate limiting (HTTP 429) and transient server errors (5xx)
        gracefully by retrying with increasing delays.
        """
        for attempt in range(max_retries):
            try:
                result = (
                    self.service.files()
                    .list(
                        q=query,
                        pageSize=page_size,
                        fields=f"nextPageToken, {fields}",
                        orderBy=order_by,
                        supportsAllDrives=True,
                        includeItemsFromAllDrives=True,
                    )
                    .execute()
                )
                return result

            except HttpError as e:
                if e.resp.status in (429, 500, 503) and attempt < max_retries - 1:
                    # Exponential backoff: 1s, 2s, 4s
                    wait_time = 2 ** attempt
                    logger.warning(
                        f"Rate limited or server error (attempt {attempt + 1}/"
                        f"{max_retries}). Retrying in {wait_time}s..."
                    )
                    time.sleep(wait_time)
                else:
                    raise

        # Should not reach here, but just in case
        raise Exception("Max retries exceeded for Drive API call")
