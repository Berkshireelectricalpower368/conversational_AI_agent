"""
LangChain Agent service for AI-powered file search.

Orchestrates the interaction between:
- Gemini LLM (via ChatGoogleGenerativeAI)
- DriveSearchTool (custom tool for Drive API)
- Conversation memory (per-session buffer)

Uses LangChain's tool calling interface to let Gemini decide
when and how to search Drive based on user queries.
"""

import json
from typing import Any, Dict, List, Optional
from collections import defaultdict
from datetime import datetime, timezone

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage, ToolMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

from backend.config import get_settings
from backend.services.drive_service import DriveService
from backend.tools.drive_search_tool import search_drive_files, set_drive_service
from backend.prompts.system_prompts import get_system_prompt
from backend.models.schemas import FileResult, SearchHistoryItem
from backend.utils.logger import get_logger

logger = get_logger(__name__)


class AgentService:
    """
    LangChain Agent that uses Gemini + DriveSearchTool for file discovery.
    
    Manages conversation memory per session and handles the full
    tool-calling loop: user query → LLM → tool call → tool result → LLM response.
    """

    def __init__(self):
        """Initialize the agent with Gemini LLM and Drive tool."""
        settings = get_settings()

        # ── Initialize Google Drive service ──────────────────
        self.drive_service = DriveService(
            service_account_source=settings.google_service_account_file,
            folder_id=settings.google_drive_folder_id,
        )

        # Connect the Drive service to the tool
        set_drive_service(self.drive_service)

        # ── Initialize Gemini LLM ────────────────────────────
        self.llm = ChatGoogleGenerativeAI(
            model=settings.gemini_model,
            google_api_key=settings.google_api_key,
            temperature=0.3,  # Lower temperature for more precise query generation
            convert_system_message_to_human=True,  # Gemini compatibility
        )

        # Bind the search tool to the LLM
        self.tools = [search_drive_files]
        self.llm_with_tools = self.llm.bind_tools(self.tools)

        # ── Conversation memory (in-memory, per session) ─────
        # Key: session_id → Value: list of messages
        self.memory: Dict[str, List] = defaultdict(list)

        # ── Search history (per session) ─────────────────────
        self.search_history: Dict[str, List[SearchHistoryItem]] = defaultdict(list)

        # Maximum messages to keep in memory per session (prevents token overflow)
        self.max_memory_messages = 20

        logger.info(f"Agent initialized with model: {settings.gemini_model}")

    async def process_query(
        self, query: str, session_id: str
    ) -> Dict[str, Any]:
        """
        Process a user's natural language query.
        
        This runs the full agent loop:
        1. Build message history with system prompt + conversation memory
        2. Send to Gemini LLM with bound tools
        3. If LLM wants to call a tool, execute it and feed results back
        4. Return the final AI response and any file results
        
        Args:
            query: Natural language search query from the user.
            session_id: Session identifier for conversation memory.
        
        Returns:
            Dict with 'message', 'files', and 'query_used' keys.
        """
        logger.info(f"Processing query for session {session_id}: '{query}'")

        try:
            # Step 1: Build the message list
            system_prompt = get_system_prompt()
            messages = [SystemMessage(content=system_prompt)]

            # Add conversation history (limited to last N messages)
            history = self.memory[session_id][-self.max_memory_messages:]
            messages.extend(history)

            # Add the current user message
            messages.append(HumanMessage(content=query))

            # Step 2: Invoke the LLM with tools
            response = self.llm_with_tools.invoke(messages)

            # Step 3: Handle tool calls (agent loop)
            files = []
            query_used = None
            max_iterations = 5  # Safety limit to prevent infinite loops

            iteration = 0
            while response.tool_calls and iteration < max_iterations:
                iteration += 1
                logger.info(f"Agent loop iteration {iteration}: {len(response.tool_calls)} tool call(s)")

                # Add AI's tool call message to the conversation
                messages.append(response)

                # Execute each tool call
                for tool_call in response.tool_calls:
                    tool_name = tool_call["name"]
                    tool_args = tool_call["args"]

                    logger.info(f"Executing tool: {tool_name} with args: {tool_args}")

                    if tool_name == "search_drive_files":
                        # Execute the search
                        tool_result = search_drive_files.invoke(tool_args)
                        query_used = tool_args.get("query", "")

                        # Parse file results from the tool output
                        try:
                            parsed = json.loads(tool_result)
                            if parsed.get("files"):
                                files = parsed["files"]
                            if parsed.get("query_used"):
                                query_used = parsed["query_used"]
                        except json.JSONDecodeError:
                            pass

                        # Add tool result message
                        messages.append(
                            ToolMessage(
                                content=tool_result,
                                tool_call_id=tool_call["id"],
                            )
                        )
                    else:
                        # Unknown tool — shouldn't happen, but handle gracefully
                        messages.append(
                            ToolMessage(
                                content=f"Unknown tool: {tool_name}",
                                tool_call_id=tool_call["id"],
                            )
                        )

                # Get the next response from the LLM
                response = self.llm_with_tools.invoke(messages)

            # Step 4: Extract the final text response
            final_message = response.content
            if isinstance(final_message, list):
                # Some models return content as a list of parts
                final_message = " ".join(
                    part.get("text", str(part)) if isinstance(part, dict) else str(part)
                    for part in final_message
                )

            # Step 5: Update conversation memory
            self.memory[session_id].append(HumanMessage(content=query))
            self.memory[session_id].append(AIMessage(content=final_message))

            # Trim memory if it exceeds the limit
            if len(self.memory[session_id]) > self.max_memory_messages:
                self.memory[session_id] = self.memory[session_id][-self.max_memory_messages:]

            # Step 6: Record in search history
            self.search_history[session_id].append(
                SearchHistoryItem(
                    query=query,
                    timestamp=datetime.now(timezone.utc).isoformat(),
                    result_count=len(files),
                )
            )

            # Step 7: Convert file dicts to FileResult models
            file_results = []
            for f in files:
                file_results.append(
                    FileResult(
                        id=f.get("id", ""),
                        name=f.get("name", "Unknown"),
                        mime_type=f.get("mimeType", ""),
                        modified_time=f.get("modifiedTime"),
                        web_view_link=f.get("webViewLink"),
                        icon_link=f.get("iconLink"),
                        size=f.get("size"),
                        thumbnail_link=f.get("thumbnailLink"),
                    )
                )

            logger.info(
                f"Query processed: {len(file_results)} files, "
                f"query_used='{query_used}'"
            )

            return {
                "message": final_message,
                "files": file_results,
                "query_used": query_used,
            }

        except Exception as e:
            error_str = str(e)
            logger.error(f"Agent processing error: {e}", exc_info=True)

            # ── Handle Gemini rate limit / quota errors ──────
            if "429" in error_str or "RESOURCE_EXHAUSTED" in error_str:
                return {
                    "message": (
                        "⏳ **API Rate Limit Reached**\n\n"
                        "The Gemini AI model has reached its usage limit for now. "
                        "This is a temporary restriction on the free tier.\n\n"
                        "**What you can do:**\n"
                        "- ⏰ Wait a minute and try again\n"
                        "- 🔄 If the daily limit is reached, it resets at midnight (Pacific Time)\n"
                        "- 💳 Upgrade to a paid plan at [Google AI Studio](https://aistudio.google.com) for higher limits\n\n"
                        "Your query has been saved — just hit retry once the limit renews!"
                    ),
                    "files": [],
                    "query_used": None,
                }

            # ── Handle other errors ──────────────────────────
            return {
                "message": (
                    f"I encountered an error while searching: {error_str}. "
                    "Please try rephrasing your query or check if the "
                    "service is properly configured."
                ),
                "files": [],
                "query_used": None,
            }

    def get_search_history(self, session_id: str) -> List[SearchHistoryItem]:
        """Get the search history for a session."""
        return self.search_history.get(session_id, [])

    def clear_session(self, session_id: str) -> None:
        """Clear conversation memory and search history for a session."""
        if session_id in self.memory:
            del self.memory[session_id]
        if session_id in self.search_history:
            del self.search_history[session_id]
        logger.info(f"Session {session_id} cleared")
