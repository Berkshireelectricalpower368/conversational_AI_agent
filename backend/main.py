"""
FastAPI backend for the Google Drive File Discovery Assistant.

Provides REST API endpoints for:
- Chat: Process natural language queries via the AI agent
- History: Retrieve search history for a session
- Health: Server status check

Run with: uvicorn backend.main:app --reload
"""

import os
from contextlib import asynccontextmanager
from typing import Optional

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from backend.config import get_settings
from backend.models.schemas import (
    ChatRequest,
    ChatResponse,
    ErrorResponse,
    SearchHistoryResponse,
)
from backend.services.agent_service import AgentService
from backend.utils.logger import get_logger

logger = get_logger(__name__)

# ── Global agent instance ────────────────────────────────────
agent_service: Optional[AgentService] = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan handler.
    
    Initializes the agent service on startup and logs shutdown.
    Using lifespan instead of deprecated @app.on_event.
    """
    global agent_service

    logger.info("=" * 60)
    logger.info("Starting Google Drive File Discovery Assistant")
    logger.info("=" * 60)

    try:
        # Initialize the agent (loads Drive service + Gemini LLM)
        agent_service = AgentService()
        logger.info("Agent service initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize agent service: {e}")
        logger.error("The server will start but queries will fail.")
        logger.error("Check your .env configuration.")

    yield  # Server is running

    logger.info("Shutting down server...")


# ── Create FastAPI app ───────────────────────────────────────
app = FastAPI(
    title="Drive Discovery Assistant API",
    description=(
        "AI-powered Google Drive file search API. "
        "Uses Gemini + LangChain to convert natural language queries "
        "into Google Drive API searches."
    ),
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",      # Swagger UI at /docs
    redoc_url="/redoc",     # ReDoc at /redoc
)

# ── CORS Configuration ──────────────────────────────────────
# Allow requests from Streamlit (runs on port 8501 by default)
# and common deployment domains
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:8501", 
        "https://drive-discovery.streamlit.app",      
        "http://localhost:3000",       # Alternative frontend port
        "https://*.streamlit.app",     # Streamlit Cloud
        "https://*.onrender.com",      # Render deployments
        "*",                           # Allow all for development
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Global Exception Handler ────────────────────────────────

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """
    Catch-all exception handler to return clean JSON errors
    instead of raw stack traces.
    """
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content=ErrorResponse(
            error="Internal server error",
            detail=str(exc) if os.getenv("LOG_LEVEL") == "DEBUG" else None,
        ).model_dump(),
    )


# ── API Endpoints ────────────────────────────────────────────

@app.get("/health", tags=["System"])
async def health_check():
    """
    Health check endpoint.
    
    Returns server status and whether the agent is properly initialized.
    Useful for deployment health checks and monitoring.
    """
    return {
        "status": "healthy",
        "agent_initialized": agent_service is not None,
        "version": "1.0.0",
    }


@app.post(
    "/api/chat",
    response_model=ChatResponse,
    tags=["Chat"],
    summary="Process a natural language search query",
    responses={
        200: {"description": "Successful search with AI response and file results"},
        400: {"model": ErrorResponse, "description": "Invalid request"},
        503: {"model": ErrorResponse, "description": "Agent not initialized"},
    },
)
async def chat(request: ChatRequest):
    """
    Main chat endpoint — processes a natural language query.
    
    The AI agent will:
    1. Understand the user's search intent
    2. Generate a Google Drive API q parameter query
    3. Search Google Drive
    4. Return a conversational response with matching files
    
    Maintains conversation context per session_id for follow-up queries.
    """
    # Check agent is ready
    if agent_service is None:
        raise HTTPException(
            status_code=503,
            detail="Agent service is not initialized. Check server logs for configuration errors.",
        )

    logger.info(f"Chat request — session: {request.session_id}, query: '{request.query}'")

    # Process the query through the AI agent
    result = await agent_service.process_query(
        query=request.query,
        session_id=request.session_id,
    )

    # Build the response
    response = ChatResponse(
        message=result["message"],
        files=result["files"],
        query_used=result.get("query_used"),
        session_id=request.session_id,
    )

    logger.info(
        f"Chat response — files: {len(response.files)}, "
        f"query_used: '{response.query_used}'"
    )

    return response


@app.get(
    "/api/history/{session_id}",
    response_model=SearchHistoryResponse,
    tags=["History"],
    summary="Get search history for a session",
)
async def get_history(session_id: str):
    """
    Retrieve the search history for a given session.
    
    Returns a list of previous searches with their queries,
    timestamps, and result counts. Used by the sidebar.
    """
    if agent_service is None:
        return SearchHistoryResponse(history=[], session_id=session_id)

    history = agent_service.get_search_history(session_id)
    return SearchHistoryResponse(history=history, session_id=session_id)


@app.delete(
    "/api/session/{session_id}",
    tags=["Session"],
    summary="Clear a session's memory and history",
)
async def clear_session(session_id: str):
    """
    Clear conversation memory and search history for a session.
    
    Used by the "New Chat" button in the frontend.
    """
    if agent_service:
        agent_service.clear_session(session_id)

    logger.info(f"Session {session_id} cleared")
    return {"status": "cleared", "session_id": session_id}


# ── Run directly (for development) ──────────────────────────
if __name__ == "__main__":
    import uvicorn

    settings = get_settings()
    uvicorn.run(
        "backend.main:app",
        host=settings.backend_host,
        port=settings.backend_port,
        reload=True,
        log_level=settings.log_level.lower(),
    )
