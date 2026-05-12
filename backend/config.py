"""
Configuration management for the Google Drive File Discovery Assistant.

Loads environment variables from .env file with validation and sensible defaults.
Uses pydantic-settings for type-safe configuration.
"""

import os
from typing import Optional
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.
    
    Required variables will raise a validation error on startup if missing,
    giving a clear message about what needs to be configured.
    """

    # ── Gemini AI ────────────────────────────────────────────
    google_api_key: str = Field(
        ...,  # Required
        description="Google AI Studio API key for Gemini"
    )
    gemini_model: str = Field(
        default="gemini-2.0-flash",
        description="Gemini model name to use for AI queries"
    )

    # ── Google Drive API ─────────────────────────────────────
    google_service_account_file: str = Field(
        ...,  # Required
        description="Path to service account JSON key file, or the JSON string itself"
    )
    google_drive_folder_id: Optional[str] = Field(
        default=None,
        description="Optional: restrict search to a specific Drive folder"
    )

    # ── Backend Server ───────────────────────────────────────
    backend_host: str = Field(default="0.0.0.0", description="Server bind host")
    backend_port: int = Field(default=8000, description="Server bind port")

    # ── Frontend ─────────────────────────────────────────────
    backend_url: str = Field(
        default="http://localhost:8000",
        description="URL of the backend API (used by frontend)"
    )

    # ── Logging ──────────────────────────────────────────────
    log_level: str = Field(default="INFO", description="Logging level")

    class Config:
        # Load variables from .env file in the project root
        env_file = ".env"
        env_file_encoding = "utf-8"
        # Allow extra fields to be ignored (e.g., from system env vars)
        extra = "ignore"


def get_settings() -> Settings:
    """
    Create and return a Settings instance.
    
    This function is called once at startup. If required environment
    variables are missing, it will raise a clear validation error.
    """
    try:
        return Settings()
    except Exception as e:
        print(f"\n{'='*60}")
        print("[!] CONFIGURATION ERROR")
        print(f"{'='*60}")
        print(f"\n{e}")
        print(f"\nMake sure you have a .env file with all required variables.")
        print(f"See .env.example for the template.\n")
        raise
