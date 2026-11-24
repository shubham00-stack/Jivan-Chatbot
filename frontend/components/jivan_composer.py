"""
JIVAN ChatGPT-Style Message Composer & File Attachment System
Features:
- ONE single rounded message composer container matching ChatGPT UX
- #212121 charcoal background (never pure black #000000)
- Layout: [ + ] [ Ask JIVAN................ ] [ Microphone ] [ Send ↑ ]
- Extreme Left: Plus (+) button opens floating dropdown menu ABOVE the composer:
  * Option 1: Add Photos & Files (system file picker for multiple images, PDFs, Word, Excel, text)
  * Option 2: Upload from Device (browse documents from device)
  * Option 3: Take Photo (camera photo capture with graceful fallback)
- Attachment Preview System:
  * Displays small image thumbnails
  * Displays document icons (PDF, Word, Excel, etc.), filenames, extensions, and file sizes
  * Small (X) remove button on each attachment
  * Dynamic vertical expansion when attachments are present
- Voice recording via Web Audio MediaRecorder
- Blue circular send button (#1D61D2) with upward arrow
- Keyboard support: Enter to send, Shift+Enter for newline
"""

import os
import base64
from pathlib import Path
import streamlit as st
import streamlit.components.v1 as components

# Declare the ChatGPT Composer custom component
_COMPONENT_DIR = Path(__file__).parent / "chatgpt_composer"
_chatgpt_composer = components.declare_component(
    "jivan_chatgpt_composer",
    path=str(_COMPONENT_DIR)
)

def format_file_size(size_bytes: int) -> str:
    """Formats file size into human-readable B, KB, or MB."""
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.1f} KB"
    else:
        return f"{size_bytes / (1024 * 1024):.1f} MB"

def get_file_type_meta(filename: str):
    """Returns (file_type, icon, extension_label) based on file extension."""
    ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
    if ext in ("png", "jpg", "jpeg", "webp", "gif"):
        return "image", "🖼️", ext.upper()
    elif ext in ("pdf",):
        return "document", "📕", "PDF"
    elif ext in ("docx", "doc"):
        return "document", "📘", "DOCX"
    elif ext in ("xlsx", "xls", "csv"):
        return "document", "📗", ext.upper()
    elif ext in ("pptx", "ppt"):
        return "document", "📙", "PPTX"
    elif ext in ("mp3", "wav", "m4a", "ogg"):
        return "audio", "🎙️", ext.upper()
    elif ext in ("txt", "md", "py", "json", "html"):
        return "document", "📄", ext.upper()
    else:
        return "document", "📁", ext.upper() if ext else "FILE"

def stage_uploaded_files(uploaded_files) -> int:
    """Safely stages multiple files into st.session_state['staged_attachments'] without duplicates."""
    if not uploaded_files:
        return 0

    if "staged_attachments" not in st.session_state:
        st.session_state["staged_attachments"] = []

    current_ids = {att["id"] for att in st.session_state["staged_attachments"]}
    added_count = 0

    if not isinstance(uploaded_files, (list, tuple)):
        uploaded_files = [uploaded_files]

    for f in uploaded_files:
        if not f:
            continue
        file_id = f"{f.name}_{f.size}"
        if file_id in current_ids:
            continue

        if f.size > 25 * 1024 * 1024:
            st.toast(f"File '{f.name}' exceeds the 25 MB limit.", icon="⚠️")
            continue

        file_type, icon, ext_label = get_file_type_meta(f.name)
        file_bytes = f.getvalue() if hasattr(f, "getvalue") else f.read()

        b64_thumb = None
        if file_type == "image":
            try:
                b64_thumb = base64.b64encode(file_bytes).decode("utf-8")
            except Exception:
                b64_thumb = None

        st.session_state["staged_attachments"].append({
            "id": file_id,
            "name": f.name,
            "size": f.size,
            "size_str": format_file_size(f.size),
            "ext": ext_label,
            "icon": icon,
            "type": file_type,
            "bytes": file_bytes,
            "b64": b64_thumb
        })
        current_ids.add(file_id)
        added_count += 1

    return added_count

def render_jivan_composer(key: str = None):
    """
    Renders ONE single rounded message composer:
    [ + ] [ Ask JIVAN................ ] [ Microphone ] [ Send ↑ ]
    Returns submission dict when user sends a message, or None.
    Uses dynamic turn-based keying to guarantee a fresh, responsive composer on every turn.
    """
    theme_mode = st.session_state.get("theme_mode", "light")
    queued = st.session_state.get("queued_prompt", "")
    
    if key is None:
        turn_id = len(st.session_state.get("messages", []))
        key = f"jivan_chatgpt_composer_turn_{turn_id}"

    # Render the ChatGPT custom composer component
    composer_data = _chatgpt_composer(
        key=key,
        theme=theme_mode,
        default_prompt=queued,
        default=None
    )
    return composer_data

def render_jivan_disclaimer():
    """Renders the standard AI disclaimer footer."""
    st.markdown(
        '<div class="gemini-disclaimer">JIVAN may display inaccurate info, including about people, so double-check its responses.</div>',
        unsafe_allow_html=True
    )

# Alias for topbar theme toggle helper
from frontend.components.jivan_chat import render_jivan_topbar_theme_toggle
