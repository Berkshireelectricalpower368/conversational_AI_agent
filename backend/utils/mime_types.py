"""
MIME type mappings for Google Drive file types.

Maps human-readable file type names to their Google Drive MIME types.
Used by the AI agent to convert user queries like "PDFs" or "spreadsheets"
into the correct mimeType filter values.
"""

# ── Complete MIME type mapping ───────────────────────────────
# Maps friendly names → Google Drive MIME type strings
MIME_TYPE_MAP = {
    # Google Workspace native types
    "google doc":        "application/vnd.google-apps.document",
    "google sheet":      "application/vnd.google-apps.spreadsheet",
    "google slide":      "application/vnd.google-apps.presentation",
    "google form":       "application/vnd.google-apps.form",
    "google drawing":    "application/vnd.google-apps.drawing",
    "google site":       "application/vnd.google-apps.site",
    "google map":        "application/vnd.google-apps.map",
    "google script":     "application/vnd.google-apps.script",
    "google folder":     "application/vnd.google-apps.folder",

    # Documents
    "pdf":               "application/pdf",
    "word":              "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "word doc":          "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "docx":              "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "doc":               "application/msword",
    "rtf":               "application/rtf",
    "text":              "text/plain",
    "txt":               "text/plain",

    # Spreadsheets
    "excel":             "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    "xlsx":              "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    "xls":               "application/vnd.ms-excel",
    "csv":               "text/csv",

    # Presentations
    "powerpoint":        "application/vnd.openxmlformats-officedocument.presentationml.presentation",
    "pptx":              "application/vnd.openxmlformats-officedocument.presentationml.presentation",
    "ppt":               "application/vnd.ms-powerpoint",

    # Images
    "jpeg":              "image/jpeg",
    "jpg":               "image/jpeg",
    "png":               "image/png",
    "gif":               "image/gif",
    "svg":               "image/svg+xml",
    "webp":              "image/webp",
    "bmp":               "image/bmp",
    "ico":               "image/x-icon",
    "tiff":              "image/tiff",

    # Videos
    "mp4":               "video/mp4",
    "avi":               "video/x-msvideo",
    "mov":               "video/quicktime",
    "wmv":               "video/x-ms-wmv",
    "mkv":               "video/x-matroska",
    "webm":              "video/webm",

    # Audio
    "mp3":               "audio/mpeg",
    "wav":               "audio/wav",
    "ogg":               "audio/ogg",
    "flac":              "audio/flac",

    # Archives
    "zip":               "application/zip",
    "rar":               "application/x-rar-compressed",
    "tar":               "application/x-tar",
    "gz":                "application/gzip",
    "7z":                "application/x-7z-compressed",

    # Code & Data
    "json":              "application/json",
    "xml":               "application/xml",
    "html":              "text/html",
    "css":               "text/css",
    "javascript":        "application/javascript",
    "python":            "text/x-python",
    "markdown":          "text/markdown",
}


# ── Reverse mapping: MIME type → display name ────────────────
# Used for showing friendly file type names in the UI
MIME_TO_DISPLAY = {
    "application/vnd.google-apps.document":     "Google Doc",
    "application/vnd.google-apps.spreadsheet":  "Google Sheet",
    "application/vnd.google-apps.presentation": "Google Slides",
    "application/vnd.google-apps.form":         "Google Form",
    "application/vnd.google-apps.drawing":      "Google Drawing",
    "application/vnd.google-apps.folder":       "Folder",
    "application/pdf":                          "PDF",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document": "Word Doc",
    "application/msword":                       "Word Doc",
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet": "Excel",
    "application/vnd.ms-excel":                 "Excel",
    "application/vnd.openxmlformats-officedocument.presentationml.presentation": "PowerPoint",
    "application/vnd.ms-powerpoint":            "PowerPoint",
    "text/plain":                               "Text File",
    "text/csv":                                 "CSV",
    "text/html":                                "HTML",
    "image/jpeg":                               "JPEG Image",
    "image/png":                                "PNG Image",
    "image/gif":                                "GIF",
    "image/svg+xml":                            "SVG",
    "video/mp4":                                "MP4 Video",
    "video/quicktime":                          "MOV Video",
    "audio/mpeg":                               "MP3 Audio",
    "application/zip":                          "ZIP Archive",
    "application/json":                         "JSON",
    "application/xml":                          "XML",
}


# ── File type → emoji icon mapping ───────────────────────────
# Used in the frontend to show icons next to file names
MIME_TO_ICON = {
    "application/vnd.google-apps.document":     "📝",
    "application/vnd.google-apps.spreadsheet":  "📊",
    "application/vnd.google-apps.presentation": "📽️",
    "application/vnd.google-apps.form":         "📋",
    "application/vnd.google-apps.drawing":      "🎨",
    "application/vnd.google-apps.folder":       "📁",
    "application/pdf":                          "📄",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document": "📝",
    "application/msword":                       "📝",
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet": "📊",
    "application/vnd.ms-excel":                 "📊",
    "application/vnd.openxmlformats-officedocument.presentationml.presentation": "📽️",
    "application/vnd.ms-powerpoint":            "📽️",
    "text/plain":                               "📃",
    "text/csv":                                 "📊",
    "image/jpeg":                               "🖼️",
    "image/png":                                "🖼️",
    "image/gif":                                "🖼️",
    "image/svg+xml":                            "🖼️",
    "video/mp4":                                "🎬",
    "video/quicktime":                          "🎬",
    "audio/mpeg":                               "🎵",
    "application/zip":                          "📦",
    "application/json":                         "📋",
}


def get_display_name(mime_type: str) -> str:
    """Get a human-readable display name for a MIME type."""
    return MIME_TO_DISPLAY.get(mime_type, mime_type.split("/")[-1].upper())


def get_icon(mime_type: str) -> str:
    """Get an emoji icon for a MIME type."""
    # Check exact match first
    if mime_type in MIME_TO_ICON:
        return MIME_TO_ICON[mime_type]
    # Fall back to category-based icons
    if mime_type.startswith("image/"):
        return "🖼️"
    if mime_type.startswith("video/"):
        return "🎬"
    if mime_type.startswith("audio/"):
        return "🎵"
    if mime_type.startswith("text/"):
        return "📃"
    return "📎"  # Default icon for unknown types


def get_mime_type_list_for_prompt() -> str:
    """
    Generate a formatted string of common MIME types for inclusion
    in the AI system prompt. Helps the LLM generate correct queries.
    """
    common_types = {
        "PDF files":         "application/pdf",
        "Google Docs":       "application/vnd.google-apps.document",
        "Google Sheets":     "application/vnd.google-apps.spreadsheet",
        "Google Slides":     "application/vnd.google-apps.presentation",
        "Word documents":    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "Excel spreadsheets":"application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        "PowerPoint":        "application/vnd.openxmlformats-officedocument.presentationml.presentation",
        "Images (JPEG)":     "image/jpeg",
        "Images (PNG)":      "image/png",
        "Videos (MP4)":      "video/mp4",
        "Text files":        "text/plain",
        "CSV files":         "text/csv",
        "Folders":           "application/vnd.google-apps.folder",
    }
    lines = [f"  - {name}: mimeType='{mime}'" for name, mime in common_types.items()]
    return "\n".join(lines)
