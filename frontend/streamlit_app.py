"""
JIVAN AI - Modern AI Chatbot Main Application Entrypoint
UI Features:
- Exact ChatGPT-style input capsule: [+] Ask JIVAN ... [🧠 Think] [🎙️] [🔵]
- Direct native file attachment picker via [+] on the left (PDF, TXT, DOC, Images, Audio)
- Native microphone voice recording with Whisper Speech-to-Text
- '🧠 Think' toggle for deep reasoning and chain-of-thought analysis
- Circular blue submit button [🔵]
- Fully connected to Groq (qwen/llama), Claude, Canva, Nano Banana, and Chroma RAG
"""

import sys
import os
import subprocess
import time
import base64
from pathlib import Path
from datetime import datetime
import streamlit as st

# Ensure project root is in sys.path
repo_root = Path(__file__).resolve().parent
if not (repo_root / "backend").exists():
    repo_root = repo_root.parent

if str(repo_root) not in sys.path:
    sys.path.insert(0, str(repo_root))

from frontend.components.jivan_theme import get_jivan_css
from frontend.components.jivan_sidebar import render_jivan_sidebar
from frontend.components.jivan_chat import render_jivan_chat_header, render_jivan_messages, render_jivan_topbar_theme_toggle
from frontend.components.jivan_composer import render_jivan_composer, render_jivan_disclaimer, format_file_size
from frontend.components.jivan_inspector import render_jivan_inspector

# Specialized Views
from frontend.components.views.knowledge_view import render_knowledge_view
from frontend.components.views.tasks_view import render_tasks_view
from frontend.components.views.templates_view import render_templates_view
from frontend.components.views.settings_view import render_settings_view
from frontend.utils.api_client import api_client

# Streamlit Page Setup
st.set_page_config(
    page_title="JIVAN - AI Assistant",
    page_icon="✦",
    layout="wide",
    initial_sidebar_state="auto"
)

@st.cache_resource
def ensure_backend_online():
    """Ensures the FastAPI backend daemon is running in cloud or single-container environments."""
    try:
        if hasattr(st, "secrets"):
            env_lines = []
            for k, v in st.secrets.items():
                if isinstance(v, str):
                    os.environ[k] = v
                    env_lines.append(f"{k}={v}")
            env_file = repo_root / ".env"
            if not env_file.exists() and env_lines:
                with open(env_file, "w", encoding="utf-8") as f:
                    f.write("\n".join(env_lines) + "\n")
    except Exception:
        pass

    health = api_client.check_health()
    if health.get("status") == "healthy":
        try:
            api_client.update_keys(
                groq_key=os.environ.get("GROQ_API_KEY"),
                gemini_key=os.environ.get("GEMINI_API_KEY"),
                anthropic_key=os.environ.get("ANTHROPIC_API_KEY"),
                provider=os.environ.get("LLM_PROVIDER")
            )
        except Exception:
            pass
        return True

    cmd = [sys.executable, "-m", "uvicorn", "backend.main:app", "--host", "127.0.0.1", "--port", "8000"]
    subprocess.Popen(cmd, cwd=str(repo_root), env=os.environ.copy())

    for _ in range(16):
        time.sleep(0.5)
        if api_client.check_health().get("status") == "healthy":
            return True
    return False

def sync_secrets_to_backend():
    """Continuously ensures keys from Streamlit Cloud Secrets or session state are pushed live to the backend."""
    try:
        api_client._sync_secrets_to_llm()
    except Exception:
        pass

def main():
    # Ensure backend is online in cloud container
    ensure_backend_online()
    sync_secrets_to_backend()

    # Initialize Session State & Theme Persistence
    theme_param = st.query_params.get("theme")
    if theme_param in ("light", "dark"):
        st.session_state["theme_mode"] = theme_param
    elif "theme_mode" not in st.session_state:
        st.session_state["theme_mode"] = "light"
    if "active_nav" not in st.session_state:
        st.session_state["active_nav"] = "Conversations"
    if "user_email" not in st.session_state:
        st.session_state["user_email"] = "shubham@jivan.ai"
    if "messages" not in st.session_state:
        st.session_state["messages"] = []
    if "conversation_id" not in st.session_state:
        st.session_state["conversation_id"] = None
    if "conversation_title" not in st.session_state:
        st.session_state["conversation_title"] = "New Chat"
    if "enable_emotional" not in st.session_state:
        st.session_state["enable_emotional"] = True
    if "enable_rag" not in st.session_state:
        st.session_state["enable_rag"] = True
    if "enable_tts" not in st.session_state:
        st.session_state["enable_tts"] = False
    if "show_inspector" not in st.session_state:
        st.session_state["show_inspector"] = False
    if "thinking_mode" not in st.session_state:
        st.session_state["thinking_mode"] = False

    # Inject Theme CSS
    theme_css = get_jivan_css(st.session_state.get("theme_mode", "light"))
    st.markdown(theme_css, unsafe_allow_html=True)

    # Render Left Sidebar
    render_jivan_sidebar()

    # Routing by Navigation State
    active_view = st.session_state.get("active_nav", "Conversations")

    if active_view in ("Knowledge", "Tasks", "Templates", "Settings"):
        col_view_empty, col_view_toggle = st.columns([0.86, 0.14])
        with col_view_toggle:
            render_jivan_topbar_theme_toggle(key=f"btn_theme_toggle_{active_view.lower()}")

    if active_view == "Knowledge":
        render_knowledge_view()

    elif active_view == "Tasks":
        render_tasks_view()

    elif active_view == "Templates":
        render_templates_view()

    elif active_view == "Settings":
        render_settings_view()

    else:
        # Default: Conversational Canvas
        show_inspector = st.session_state.get("show_inspector", False)

        if show_inspector:
            col_main, col_side = st.columns([0.72, 0.28], gap="medium")
        else:
            col_main = st.container()
            col_side = None

        with col_main:
            # 1. Top Navigation Bar
            render_jivan_chat_header(st.session_state.get("conversation_title", "New Chat"))

            # 2. Conversational Message Stream or Hero Welcome State
            render_jivan_messages()

            # 3. Modern ChatGPT-Style Message Composer: [+] [Ask JIVAN................] [🎙️] [🔵 ↑]
            composer_data = render_jivan_composer()

            # 4. AI Disclaimer footer
            render_jivan_disclaimer()

            # Extract prompt, direct attachments, and voice memo
            user_text = None
            staged_attachments = list(st.session_state.get("staged_attachments", []))
            audio_file = None

            if "queued_prompt" in st.session_state and st.session_state["queued_prompt"]:
                user_text = st.session_state.pop("queued_prompt")

            elif composer_data and isinstance(composer_data, dict):
                sub_id = composer_data.get("id")
                last_sub_id = st.session_state.get("last_processed_composer_id")
                if sub_id and sub_id != last_sub_id:
                    st.session_state["last_processed_composer_id"] = sub_id
                    user_text = composer_data.get("text", "").strip() or None
                    raw_attachments = composer_data.get("attachments", []) or []
                    for att in raw_attachments:
                        b64 = att.get("base64", "")
                        file_bytes = base64.b64decode(b64) if b64 else b""
                        staged_attachments.append({
                            "id": f"{att.get('name', 'file')}_{len(file_bytes)}",
                            "name": att.get("name", "file"),
                            "size": att.get("size", len(file_bytes)),
                            "size_str": format_file_size(att.get("size", len(file_bytes))),
                            "type": att.get("type", "document"),
                            "ext": att.get("ext", ""),
                            "bytes": file_bytes
                        })

            # Process submission if message text, staged attachments, or audio exists
            if user_text or staged_attachments or audio_file:
                time_str = datetime.now().strftime("%I:%M %p")
                user_email = st.session_state.get("user_email", "shubham@jivan.ai")
                conv_id = st.session_state.get("conversation_id")
                is_thinking = st.session_state.get("thinking_mode", False)

                # Update conversation title if starting fresh
                if not st.session_state["messages"]:
                    title_candidate = user_text or (staged_attachments[0]["name"] if staged_attachments else "Voice Memo")
                    short_title = title_candidate[:24] + ("..." if len(title_candidate) > 24 else "")
                    st.session_state["conversation_title"] = short_title

                # ---------------------------------------------------------
                # A. Process Attached Documents (PDF, TXT, DOCX, XLSX, etc.) via RAG
                # ---------------------------------------------------------
                doc_items = [att for att in staged_attachments if att.get("type") == "document"]
                if doc_items:
                    with st.spinner(f"Indexing {len(doc_items)} attached document(s)..."):
                        payload = [(d["name"], d["bytes"]) for d in doc_items]
                        api_client.upload_multiple_documents(payload)

                    doc_names = ", ".join([d["name"] for d in doc_items])
                    st.session_state["messages"].append({
                        "role": "user",
                        "content": f"📎 Attached {len(doc_items)} file(s): `{doc_names}`" + (f"\n\n{user_text}" if user_text else ""),
                        "modality": "document",
                        "timestamp": time_str
                    })

                    with st.spinner("Analyzing document insights with AI..."):
                        query = user_text or f"Please summarize the main insights from: {doc_names}"
                        if is_thinking:
                            query = f"[Deep Thinking Mode Active]\n{query}"
                        res = api_client.send_chat_message(
                            message=query,
                            conversation_id=conv_id,
                            enable_emotional_support=False,
                            enable_rag=True,
                            user_email=user_email
                        )
                        st.session_state["conversation_id"] = res["conversation_id"]
                        st.session_state["messages"].append({
                            "id": res["message_id"],
                            "role": "assistant",
                            "content": res["response"],
                            "modality": "text",
                            "timestamp": datetime.now().strftime("%I:%M %p"),
                            "metadata": {
                                "citations": res.get("citations", []),
                                "thinking_active": is_thinking,
                                "specialist": "RAG Knowledge Specialist"
                            }
                        })
                    # Clear staged attachments
                    st.session_state["staged_attachments"] = []
                    st.rerun()

                # ---------------------------------------------------------
                # B. Process Attached Images (PNG, JPG, JPEG, WEBP, GIF)
                # ---------------------------------------------------------
                img_items = [att for att in staged_attachments if att.get("type") == "image"]
                if img_items:
                    for img in img_items:
                        img_prompt = user_text or "Please analyze and describe this visual in detail."
                        with st.spinner(f"Analyzing visual: {img['name']}..."):
                            res = api_client.send_image_message(
                                file_bytes=img["bytes"],
                                filename=img["name"],
                                prompt=img_prompt,
                                conversation_id=conv_id
                            )
                            st.session_state["conversation_id"] = res["conversation_id"]
                            st.session_state["messages"].append({
                                "role": "user",
                                "content": f"🖼️ Analyzed visual `{img['name']}`: {img_prompt}",
                                "modality": "image",
                                "timestamp": time_str
                            })
                            st.session_state["messages"].append({
                                "id": res["message_id"],
                                "role": "assistant",
                                "content": res["response"],
                                "modality": "text",
                                "timestamp": datetime.now().strftime("%I:%M %p"),
                                "metadata": {"thinking_active": is_thinking}
                            })
                    # Clear staged attachments
                    st.session_state["staged_attachments"] = []
                    st.rerun()

                # ---------------------------------------------------------
                # C. Process Voice Recording (from mic) or Audio Files
                # ---------------------------------------------------------
                aud_to_process = []
                if audio_file:
                    aud_to_process.append(("voice_query.wav", audio_file.getvalue()))
                for att in staged_attachments:
                    if att.get("type") == "audio":
                        aud_to_process.append((att["name"], att["bytes"]))

                if aud_to_process:
                    for name, bts in aud_to_process:
                        with st.spinner("Transcribing speech with Whisper..."):
                            res = api_client.send_audio_message(
                                file_bytes=bts,
                                filename=name,
                                conversation_id=conv_id,
                                enable_tts=st.session_state.get("enable_tts", False)
                            )
                            st.session_state["conversation_id"] = res["conversation_id"]
                            st.session_state["messages"].append({
                                "role": "user",
                                "content": f"🎙️ Audio memo: *\"{res.get('transcript', '')}\"*",
                                "modality": "audio",
                                "timestamp": time_str
                            })
                            st.session_state["messages"].append({
                                "id": res["message_id"],
                                "role": "assistant",
                                "content": res["response"],
                                "modality": "text",
                                "audio_base64": res.get("audio_base64"),
                                "timestamp": datetime.now().strftime("%I:%M %p"),
                                "metadata": {"thinking_active": is_thinking}
                            })
                    # Clear staged attachments
                    st.session_state["staged_attachments"] = []
                    st.rerun()

                # ---------------------------------------------------------
                # D. Standard Text Query (with optional Thinking Mode)
                # ---------------------------------------------------------
                if user_text:
                    st.session_state["messages"].append({
                        "role": "user",
                        "content": user_text,
                        "modality": "text",
                        "timestamp": time_str
                    })

                    query_to_send = user_text
                    if is_thinking:
                        query_to_send = f"[Deep Thinking Mode: Provide comprehensive step-by-step reasoning and analytical clarity]\n\n{user_text}"

                    with st.spinner("Thinking..." if not is_thinking else "🧠 Reasoning deeply..."):
                        try:
                            res = api_client.send_chat_message(
                                message=query_to_send,
                                conversation_id=conv_id,
                                enable_emotional_support=st.session_state.get("enable_emotional", True),
                                enable_rag=st.session_state.get("enable_rag", True),
                                enable_tts=st.session_state.get("enable_tts", False),
                                user_email=user_email
                            )

                            st.session_state["conversation_id"] = res["conversation_id"]

                            st.session_state["messages"].append({
                                "id": res.get("message_id"),
                                "role": "assistant",
                                "content": res.get("response", "No response generated."),
                                "modality": "text",
                                "timestamp": datetime.now().strftime("%I:%M %p"),
                                "audio_base64": res.get("audio_base64"),
                                "generated_file": res.get("generated_file"),
                                "metadata": {
                                    "intent": res.get("intent"),
                                    "citations": res.get("citations", []),
                                    "model": res.get("model_used"),
                                    "specialist": res.get("specialist"),
                                    "generated_file": res.get("generated_file"),
                                    "thinking_active": is_thinking
                                }
                            })

                        except Exception as e:
                            st.error(f"Error communicating with backend: {e}")
                            st.session_state["messages"].append({
                                "role": "assistant",
                                "content": f"⚠️ An error occurred while generating response: {e}. Please try again.",
                                "modality": "text",
                                "timestamp": datetime.now().strftime("%I:%M %p"),
                                "metadata": {"error": str(e)}
                            })
                        finally:
                            # Clear staged attachments and trigger clean rerun
                            st.session_state["staged_attachments"] = []
                            st.rerun()

        if show_inspector and col_side:
            with col_side:
                render_jivan_inspector()

if __name__ == "__main__":
    main()
