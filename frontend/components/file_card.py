"""
File card component for displaying Google Drive search results.

Renders each file as a styled HTML card with:
- File icon (emoji based on MIME type)
- File name
- File type badge
- Modified date
- Clickable Google Drive link
- File size
"""

import streamlit as st
from datetime import datetime, timezone
from typing import Dict, Optional


# ── MIME type → emoji icon mapping ───────────────────────────
ICON_MAP = {
    "application/pdf":                          "📄",
    "application/vnd.google-apps.document":     "📝",
    "application/vnd.google-apps.spreadsheet":  "📊",
    "application/vnd.google-apps.presentation": "📽️",
    "application/vnd.google-apps.form":         "📋",
    "application/vnd.google-apps.folder":       "📁",
    "application/vnd.google-apps.drawing":      "🎨",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document": "📝",
    "application/msword":                       "📝",
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet": "📊",
    "application/vnd.ms-excel":                 "📊",
    "application/vnd.openxmlformats-officedocument.presentationml.presentation": "📽️",
    "text/plain":                               "📃",
    "text/csv":                                 "📊",
    "application/zip":                          "📦",
    "application/json":                         "📋",
}

# ── MIME type → display name mapping ─────────────────────────
TYPE_NAMES = {
    "application/pdf":                          "PDF",
    "application/vnd.google-apps.document":     "Google Doc",
    "application/vnd.google-apps.spreadsheet":  "Google Sheet",
    "application/vnd.google-apps.presentation": "Slides",
    "application/vnd.google-apps.form":         "Form",
    "application/vnd.google-apps.folder":       "Folder",
    "application/vnd.google-apps.drawing":      "Drawing",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document": "Word",
    "application/msword":                       "Word",
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet": "Excel",
    "application/vnd.ms-excel":                 "Excel",
    "application/vnd.openxmlformats-officedocument.presentationml.presentation": "PowerPoint",
    "text/plain":                               "Text",
    "text/csv":                                 "CSV",
    "application/zip":                          "ZIP",
    "application/json":                         "JSON",
}

# ── MIME type → badge color mapping ──────────────────────────
TYPE_COLORS = {
    "PDF":          ("#FF6B6B", "#FFF5F5"),
    "Google Doc":   ("#4285F4", "#E8F0FE"),
    "Google Sheet": ("#34A853", "#E6F4EA"),
    "Slides":       ("#FBBC04", "#FEF7E0"),
    "Form":         ("#7B1FA2", "#F3E5F5"),
    "Folder":       ("#607D8B", "#ECEFF1"),
    "Word":         ("#2B579A", "#E8EEF7"),
    "Excel":        ("#217346", "#E2F0D9"),
    "PowerPoint":   ("#D24726", "#FCE4EC"),
    "Text":         ("#78909C", "#ECEFF1"),
    "CSV":          ("#00897B", "#E0F2F1"),
    "ZIP":          ("#8D6E63", "#EFEBE9"),
    "JSON":         ("#FF7043", "#FBE9E7"),
}


def _get_icon(mime_type: str) -> str:
    """Get emoji icon for a MIME type."""
    if mime_type in ICON_MAP:
        return ICON_MAP[mime_type]
    if mime_type.startswith("image/"):
        return "🖼️"
    if mime_type.startswith("video/"):
        return "🎬"
    if mime_type.startswith("audio/"):
        return "🎵"
    if mime_type.startswith("text/"):
        return "📃"
    return "📎"


def _get_type_name(mime_type: str) -> str:
    """Get human-readable type name."""
    if mime_type in TYPE_NAMES:
        return TYPE_NAMES[mime_type]
    if mime_type.startswith("image/"):
        return "Image"
    if mime_type.startswith("video/"):
        return "Video"
    if mime_type.startswith("audio/"):
        return "Audio"
    return mime_type.split("/")[-1].upper()[:10]


def _format_date(date_str: Optional[str]) -> str:
    """Convert ISO date to human-readable relative time."""
    if not date_str:
        return "Unknown date"
    try:
        dt = datetime.fromisoformat(date_str.replace("Z", "+00:00"))
        now = datetime.now(timezone.utc)
        diff = now - dt

        if diff.days == 0:
            hours = diff.seconds // 3600
            if hours == 0:
                minutes = diff.seconds // 60
                return f"{minutes}m ago" if minutes > 0 else "Just now"
            return f"{hours}h ago"
        elif diff.days == 1:
            return "Yesterday"
        elif diff.days < 7:
            return f"{diff.days}d ago"
        elif diff.days < 30:
            weeks = diff.days // 7
            return f"{weeks}w ago"
        elif diff.days < 365:
            months = diff.days // 30
            return f"{months}mo ago"
        else:
            return dt.strftime("%b %d, %Y")
    except Exception:
        return date_str[:10] if len(date_str) >= 10 else date_str


def _format_size(size_str: Optional[str]) -> str:
    """Convert bytes to human-readable file size."""
    if not size_str:
        return ""
    try:
        size = int(size_str)
        if size < 1024:
            return f"{size} B"
        elif size < 1024 * 1024:
            return f"{size / 1024:.1f} KB"
        elif size < 1024 * 1024 * 1024:
            return f"{size / (1024 * 1024):.1f} MB"
        else:
            return f"{size / (1024 * 1024 * 1024):.1f} GB"
    except (ValueError, TypeError):
        return ""


def render_file_card(file: Dict) -> None:
    """
    Render a single file result as a styled card.
    
    Args:
        file: Dict with keys: name, mime_type, modified_time,
              web_view_link, size, icon_link, thumbnail_link
    """
    name = file.get("name", "Unknown file")
    mime_type = file.get("mime_type", "")
    modified = _format_date(file.get("modified_time"))
    link = file.get("web_view_link", "")
    size = _format_size(file.get("size"))
    icon = _get_icon(mime_type)
    type_name = _get_type_name(mime_type)

    # Get badge colors
    colors = TYPE_COLORS.get(type_name, ("#90A4AE", "#ECEFF1"))
    badge_color = colors[0]
    badge_bg = colors[1]

    # Build the file card HTML
    size_html = f'<span class="file-size">{size}</span>' if size else ""

    card_html = f"""
    <div class="file-card">
        <div class="file-card-left">
            <div class="file-icon">{icon}</div>
            <div class="file-info">
                <div class="file-name" title="{name}">{name}</div>
                <div class="file-meta">
                    <span class="file-badge" style="background:{badge_bg}; color:{badge_color}; border: 1px solid {badge_color}33;">
                        {type_name}
                    </span>
                    <span class="file-date">📅 {modified}</span>
                    {size_html}
                </div>
            </div>
        </div>
        <div class="file-card-right">
            <a href="{link}" target="_blank" rel="noopener noreferrer" class="file-link">
                Open in Drive ↗
            </a>
        </div>
    </div>
    """

    st.markdown(card_html, unsafe_allow_html=True)


def render_file_results(files: list) -> None:
    """
    Render a list of file results as styled cards.
    
    Args:
        files: List of file dicts from the API response.
    """
    if not files:
        return

    st.markdown(
        f'<div class="results-header">📋 Found {len(files)} file(s)</div>',
        unsafe_allow_html=True,
    )

    for file in files:
        render_file_card(file)
