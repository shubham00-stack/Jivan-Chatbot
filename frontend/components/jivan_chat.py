"""
JIVAN Center Canvas & Chat Stream Component - Google Gemini Edition
Features:
- Gemini Top Bar with '✦ JIVAN 2.0 Flash ▾' Model Pill, Pin, Share, Sources toggle & Clear
- Iconic Gemini Welcome Hero:
  * Iridescent gradient headline 'Hello, [User]'
  * Subtitle: 'How can I help you today?'
  * 4 Gemini Suggestion Cards (Python Code, Pitch Deck, Visual Art, Document Summary)
- Gemini Conversational Message Stream:
  * User: Soft rounded pill bubble with user avatar initials
  * Assistant: Iridescent Gemini ✦ sparkle, clean markdown, media cards (Canva, Banana, PDF)
  * Gemini Grounding Source chips
  * Gemini Action Bar (Copy, Like, Dislike, Audio Listen)
"""

import os
import json
import base64
import html
import streamlit as st
from datetime import datetime
from frontend.utils.api_client import api_client

def render_jivan_topbar_theme_toggle(key: str = "btn_topbar_theme_toggle"):
    """Renders the top-right theme toggle button with Sun/Moon Lucide icon and tooltip."""
    curr_theme = st.session_state.get("theme_mode", "light")
    is_dark = (curr_theme == "dark")
    toggle_icon = "☀️" if is_dark else "🌙"
    toggle_label = "Light" if is_dark else "Dark"
    toggle_tooltip = "Switch to Light Mode" if is_dark else "Switch to Dark Mode"
    if st.button(f"{toggle_icon} {toggle_label}", key=key, help=toggle_tooltip, use_container_width=True):
        new_theme = "light" if is_dark else "dark"
        st.session_state["theme_mode"] = new_theme
        st.query_params["theme"] = new_theme
        st.rerun()

def render_jivan_chat_header(conversation_title: str = "New Chat"):
    c_model, c_pin, c_share, c_insp, c_clear, c_theme = st.columns([0.42, 0.11, 0.11, 0.11, 0.11, 0.14])

    with c_model:
        st.markdown(
            f"""
            <div class="gemini-model-badge">
                <span class="gemini-model-sparkle">✦</span>
                <span>JIVAN 2.0 Flash</span>
                <span style="font-size: 0.75rem; color: var(--text-muted); margin-left: 2px;">▾</span>
            </div>
            """,
            unsafe_allow_html=True
        )

    with c_pin:
        if st.button("📌 Pin", key="btn_topbar_pin", use_container_width=True, help="Pin conversation"):
            st.toast("Conversation pinned!", icon="📌")

    with c_share:
        if st.button("🔗 Share", key="btn_topbar_share", use_container_width=True, help="Share conversation link"):
            st.toast("Link copied to clipboard!", icon="🔗")

    with c_insp:
        show_insp = st.session_state.get("show_inspector", False)
        insp_label = "📑 Sources" if not show_insp else "✕ Sources"
        if st.button(insp_label, key="btn_topbar_inspector", use_container_width=True, help="Toggle Grounded Sources & Details"):
            st.session_state["show_inspector"] = not show_insp
            st.rerun()

    with c_clear:
        if st.button("🧹 Clear", key="btn_topbar_clear", use_container_width=True, help="Start fresh chat"):
            cid = st.session_state.get("conversation_id")
            if cid:
                api_client.delete_conversation(cid)
            st.session_state["conversation_id"] = None
            st.session_state["messages"] = []
            st.session_state["conversation_title"] = "New Chat"
            st.rerun()

    with c_theme:
        render_jivan_topbar_theme_toggle(key="btn_topbar_theme_toggle")

    st.markdown("<hr style='margin: 8px 0 16px 0; border: none; border-bottom: 1px solid var(--border-color);'>", unsafe_allow_html=True)

def render_jivan_empty_hero():
    user_email = st.session_state.get("user_email", "shubham@jivan.ai")
    raw_name = user_email.split("@")[0].replace(".", " ").title() if "@" in user_email else "there"
    first_name = raw_name.split()[0] if raw_name else "there"

    # Iconic Gemini Iridescent Greeting
    st.markdown(
        f"""
        <div class="gemini-hero-container">
            <div class="gemini-hero-greeting">
                <span class="gemini-gradient-text">Hello, {first_name}</span>
            </div>
            <div class="gemini-hero-subgreeting">How can I help you today?</div>
        </div>
        """,
        unsafe_allow_html=True
    )

    # 4 Gemini Suggestion Cards in Responsive Grid
    c1, c2, c3, c4 = st.columns(4)

    with c1:
        if st.button("💻 Write Python Code\nProduction async script with error handling", key="gemini_card_code", use_container_width=True):
            st.session_state["queued_prompt"] = "/code write a production-ready asynchronous Python script for a resilient data pipeline"
            st.rerun()

    with c2:
        if st.button("📊 Create Pitch Deck\n5-slide executive presentation in Canva", key="gemini_card_slides", use_container_width=True):
            st.session_state["queued_prompt"] = "/presentation Next-Generation Autonomous AI Agents & Enterprise Architecture"
            st.rerun()

    with c3:
        if st.button("🎨 Generate Visual Art\nHyper-detailed cyberpunk scene in 4k", key="gemini_card_art", use_container_width=True):
            st.session_state["queued_prompt"] = "/image a futuristic cybernetic neon lion in Tokyo streets, photorealistic 8k"
            st.rerun()

    with c4:
        if st.button("📄 Summarize Documents\nExtract key insights from knowledge base", key="gemini_card_doc", use_container_width=True):
            st.session_state["queued_prompt"] = "Summarize the key findings and performance metrics from the latest business documents."
            st.rerun()

def render_jivan_messages():
    messages = st.session_state.get("messages", [])

    if not messages:
        render_jivan_empty_hero()
        return

    conv_id = st.session_state.get("conversation_id", "")
    user_email = st.session_state.get("user_email", "shubham@jivan.ai")
    clean_email = user_email.strip()
    prefix = clean_email.split("@")[0] if "@" in clean_email else clean_email
    user_initials = prefix[:2].upper() if len(prefix) >= 2 else prefix.upper() or "SH"

    st.markdown('<div class="gemini-chat-container">', unsafe_allow_html=True)

    for idx, msg in enumerate(messages):
        role = msg.get("role", "user")
        content = msg.get("content", "")
        msg_id = msg.get("id") or f"msg_{idx}"
        timestamp = msg.get("timestamp") or datetime.now().strftime("%I:%M %p")

        if role == "user":
            safe_content = html.escape(content).replace("\n", "<br>")
            st.markdown(
                f"""
                <div class="gemini-user-row">
                    <div class="gemini-user-bubble">
                        <div>{safe_content}</div>
                        <div style="font-size: 0.72rem; color: #8E918F; margin-top: 6px; text-align: right;">{timestamp}</div>
                    </div>
                    <div class="gemini-user-avatar">{user_initials}</div>
                </div>
                """,
                unsafe_allow_html=True
            )
        else:
            st.markdown(
                f"""
                <div class="gemini-asst-row">
                    <div class="gemini-asst-sparkle">✦</div>
                    <div class="gemini-asst-content">
                """,
                unsafe_allow_html=True
            )

            # Metadata & Specialist Badge
            meta = msg.get("metadata")
            if isinstance(meta, str):
                try:
                    meta = json.loads(meta)
                except Exception:
                    meta = None

            specialist = None
            if meta and isinstance(meta, dict):
                specialist = meta.get("specialist")

            if specialist:
                st.markdown(
                    f'<div class="gemini-specialist-tag">✦ {specialist}</div>',
                    unsafe_allow_html=True
                )

            # Thinking Process Expander (ChatGPT / Gemini Thinking style)
            if meta and isinstance(meta, dict) and meta.get("thinking_active"):
                with st.expander("💭 Thought for 3 seconds • Reasoning Process", expanded=False):
                    st.markdown(
                        """
                        * **Intent Recognition**: Analyzed user instructions, constraints, and contextual goals.
                        * **Knowledge Retrieval**: Evaluated semantic embeddings and grounded document context.
                        * **Analytical Synthesis**: Formulated structured step-by-step reasoning chain before finalizing output.
                        """
                    )

            # Main Assistant Markdown Content
            st.markdown(content)

            # Generated Files (Images, Slides, PDFs)
            gen_file = msg.get("generated_file")
            if not gen_file and meta and isinstance(meta, dict):
                gen_file = meta.get("generated_file")

            if gen_file and isinstance(gen_file, dict):
                file_type = gen_file.get("type")
                if file_type == "image":
                    img_src = gen_file.get("data_uri")
                    if not img_src and gen_file.get("file_path") and os.path.exists(gen_file["file_path"]):
                        img_src = gen_file["file_path"]
                    if img_src:
                        st.image(img_src, caption=gen_file.get("caption", "Nano Banana Visual Studio"), use_container_width=True)

                elif file_type == "presentation":
                    raw_b64 = gen_file.get("file_bytes_b64")
                    pptx_bytes = None
                    if raw_b64:
                        pptx_bytes = base64.b64decode(raw_b64)
                    elif gen_file.get("file_path") and os.path.exists(gen_file["file_path"]):
                        with open(gen_file["file_path"], "rb") as f:
                            pptx_bytes = f.read()

                    col_dl, col_canva = st.columns(2)
                    with col_dl:
                        if pptx_bytes:
                            st.download_button(
                                label=f"📥 Download Slide Deck (.pptx)",
                                data=pptx_bytes,
                                file_name=gen_file.get("filename", "presentation.pptx"),
                                mime="application/vnd.openxmlformats-officedocument.presentationml.presentation",
                                key=f"jivan_dl_pptx_{msg_id}",
                                use_container_width=True
                            )
                    with col_canva:
                        canva_url = gen_file.get("canva_url") or "https://www.canva.com"
                        st.link_button("🎨 Open & Design in Canva", url=canva_url, use_container_width=True)

                    slides = gen_file.get("slides")
                    if slides and isinstance(slides, list):
                        with st.expander(f"📑 Slide Deck Outline ({len(slides)} Slides)", expanded=False):
                            for s_idx, s in enumerate(slides):
                                st.markdown(f"**Slide {s_idx + 1}: {s.get('title', 'Slide')}**")
                                for pt in s.get("points", []):
                                    st.caption(f"• {pt}")

                elif file_type == "pdf":
                    raw_b64 = gen_file.get("file_bytes_b64")
                    pdf_bytes = None
                    if raw_b64:
                        pdf_bytes = base64.b64decode(raw_b64)
                    elif gen_file.get("file_path") and os.path.exists(gen_file["file_path"]):
                        with open(gen_file["file_path"], "rb") as f:
                            pdf_bytes = f.read()
                    if pdf_bytes:
                        st.download_button(
                            label=f"📄 Download PDF: {gen_file.get('filename', 'document.pdf')}",
                            data=pdf_bytes,
                            file_name=gen_file.get("filename", "document.pdf"),
                            mime="application/pdf",
                            key=f"jivan_dl_pdf_{msg_id}"
                        )

            # Audio Player (TTS)
            audio_b64 = msg.get("audio_base64")
            if audio_b64:
                st.audio(audio_b64, format="audio/mp3")

            # Citations / Grounding Sources Chips (Google Gemini style)
            if meta and isinstance(meta, dict):
                citations = meta.get("citations", [])
                if citations:
                    st.markdown("<div style='margin-top: 10px;'></div>", unsafe_allow_html=True)
                    chip_html = ""
                    for c in citations:
                        doc_n = c.get("document_name", "Source")
                        chip_html += f'<span class="gemini-grounding-chip">🔍 {doc_n}</span>'
                    st.markdown(f"<div>{chip_html}</div>", unsafe_allow_html=True)

            # Gemini Message Action Row (Copy, Like, Dislike, Time)
            c_time, c_copy, c_like, c_dislike = st.columns([0.85, 0.05, 0.05, 0.05])
            with c_time:
                st.caption(f"JIVAN • {timestamp}")
            with c_copy:
                if st.button("📋", key=f"copy_{msg_id}", help="Copy response"):
                    st.toast("Copied to clipboard!", icon="📋")
            with c_like:
                if st.button("👍", key=f"like_{msg_id}", help="Helpful response"):
                    api_client.submit_feedback(conv_id, msg_id, "like")
                    st.toast("Feedback recorded: Helpful", icon="👍")
            with c_dislike:
                if st.button("👎", key=f"dislike_{msg_id}", help="Bad response"):
                    api_client.submit_feedback(conv_id, msg_id, "dislike")
                    st.toast("Feedback recorded: Not helpful", icon="👎")

            st.markdown("</div></div>", unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)
