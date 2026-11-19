"""
JIVAN Enterprise AI Assistant - Main Application Entrypoint
Features:
- Dynamic Theme Switcher: Bright Mode (pure white canvas & white input) vs. Dark Mode (obsidian)
- Left Sidebar with real interactive navigation (Conversations, Knowledge, Tasks, Templates, Settings)
- Bottom-Left Real Working Email Login with active user session
- Fixed position Right Inspector Panel (Sources & Details)
- Non-overlapping floating composer with file attachments, voice notes, and quick action chips
- Powered by Groq (qwen/qwen3.8-27b), MySQL 8.0, and Chroma RAG
"""

import sys
from pathlib import Path
from datetime import datetime
import streamlit as st

# Ensure project root is in sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from frontend.components.jivan_theme import get_jivan_css
from frontend.components.jivan_sidebar import render_jivan_sidebar
from frontend.components.jivan_chat import render_jivan_chat_header, render_jivan_messages
from frontend.components.jivan_composer import render_jivan_composer
from frontend.components.jivan_inspector import render_jivan_inspector

# Views
from frontend.components.views.knowledge_view import render_knowledge_view
from frontend.components.views.tasks_view import render_tasks_view
from frontend.components.views.templates_view import render_templates_view
from frontend.components.views.settings_view import render_settings_view
from frontend.utils.api_client import api_client

# Streamlit Page Setup
st.set_page_config(
    page_title="JIVAN - Enterprise AI Assistant",
    page_icon="🍃",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize Session State
if "theme_mode" not in st.session_state:
    st.session_state["theme_mode"] = "bright"
if "active_nav" not in st.session_state:
    st.session_state["active_nav"] = "Conversations"
if "user_email" not in st.session_state:
    st.session_state["user_email"] = "shubham@jivan.ai"
if "messages" not in st.session_state:
    st.session_state["messages"] = []
if "conversation_id" not in st.session_state:
    st.session_state["conversation_id"] = None
if "conversation_title" not in st.session_state:
    st.session_state["conversation_title"] = "Q2 Sales Overview"
if "enable_emotional" not in st.session_state:
    st.session_state["enable_emotional"] = True
if "enable_rag" not in st.session_state:
    st.session_state["enable_rag"] = True
if "enable_tts" not in st.session_state:
    st.session_state["enable_tts"] = False

# Inject Dynamic JIVAN Theme CSS
theme_css = get_jivan_css(st.session_state.get("theme_mode", "bright"))
st.markdown(theme_css, unsafe_allow_html=True)

# Render Left Sidebar (Navigation, Themes, Recent Chats, Email Login)
render_jivan_sidebar()

# Routing by Navigation State
active_view = st.session_state.get("active_nav", "Conversations")

if active_view == "Knowledge":
    render_knowledge_view()

elif active_view == "Tasks":
    render_tasks_view()

elif active_view == "Templates":
    render_templates_view()

elif active_view == "Settings":
    render_settings_view()

else:
    # Default: "Conversations" (2-column layout: Center Canvas + Fixed Right Inspector)
    col_canvas, col_inspector = st.columns([0.72, 0.28], gap="medium")

    with col_canvas:
        # 1. Top Bar
        render_jivan_chat_header(st.session_state.get("conversation_title", "Q2 Sales Overview"))

        # 2. Messages Stream or Hero Empty State
        render_jivan_messages()

        # 3. Clean Non-Overlapping Floating Composer Tools
        render_jivan_composer()

        # 4. Pure White High-Visibility Chat Input
        chat_prompt = st.chat_input("Ask a question...")

        # Process queued prompt (e.g. from pills or templates) or direct text
        user_text = None
        if "queued_prompt" in st.session_state and st.session_state["queued_prompt"]:
            user_text = st.session_state.pop("queued_prompt")
        elif chat_prompt:
            user_text = chat_prompt

        if user_text:
            time_str = datetime.now().strftime("%I:%M %p")
            user_email = st.session_state.get("user_email", "shubham@jivan.ai")

            # Update conversation title if starting fresh
            if not st.session_state["messages"]:
                short_title = user_text[:24] + ("..." if len(user_text) > 24 else "")
                st.session_state["conversation_title"] = short_title

            # Append User Message immediately
            st.session_state["messages"].append({
                "role": "user",
                "content": user_text,
                "modality": "text",
                "timestamp": time_str
            })

            with st.spinner("Thinking..."):
                try:
                    res = api_client.send_chat_message(
                        message=user_text,
                        conversation_id=st.session_state.get("conversation_id"),
                        enable_emotional_support=st.session_state.get("enable_emotional", True),
                        enable_rag=st.session_state.get("enable_rag", True),
                        enable_tts=st.session_state.get("enable_tts", False),
                        user_email=user_email
                    )

                    st.session_state["conversation_id"] = res["conversation_id"]

                    # Append Assistant Response
                    st.session_state["messages"].append({
                        "id": res["message_id"],
                        "role": "assistant",
                        "content": res["response"],
                        "modality": "text",
                        "timestamp": datetime.now().strftime("%I:%M %p"),
                        "audio_base64": res.get("audio_base64"),
                        "generated_file": res.get("generated_file"),
                        "metadata": {
                            "intent": res.get("intent"),
                            "citations": res.get("citations", []),
                            "model": res.get("model_used"),
                            "specialist": res.get("specialist"),
                            "generated_file": res.get("generated_file")
                        }
                    })
                    st.rerun()

                except Exception as e:
                    st.error(f"Error communicating with backend: {e}")

    with col_inspector:
        # Fixed-position Right Drawer
        render_jivan_inspector()
