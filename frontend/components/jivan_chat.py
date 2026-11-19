"""
JIVAN Center Canvas & Chat Stream Component
Features:
- Top bar with conversation title ('Q2 Sales Overview ˅'), timestamp, and action icons (pin, share, more)
- Hero empty state with mint chat bubble, 'Ask a question' headline, and 3 suggestion pills:
  * 📊 Summarize Q2 performance
  * ⏱️ Compare product metrics
  * 👤 What are key customer themes?
- Chat message feed with soft light blue user bubble & dynamic user initials avatar
- Assistant message with navy sparkle AI badge ✦, action icons (copy, thumbs up, thumbs down)
- Seamless rendering of generated AI images, PDF downloads, citations, and audio
"""

import os
import json
import base64
import html
import streamlit as st
from datetime import datetime
from frontend.utils.api_client import api_client

def render_jivan_chat_header(conversation_title: str = "Q2 Sales Overview"):
    time_str = datetime.now().strftime("%I:%M %p")
    c_title, c_pin, c_share, c_clear = st.columns([0.55, 0.15, 0.15, 0.15])

    with c_title:
        st.markdown(
            f"""
            <div>
                <div class="jivan-topbar-title">
                    <span>{conversation_title}</span>
                    <span style="font-size: 0.8rem; color: #94A3B8;">˅</span>
                </div>
                <div class="jivan-topbar-subtitle">Created today at {time_str}</div>
            </div>
            """,
            unsafe_allow_html=True
        )

    with c_pin:
        if st.button("📌 Pin", key="btn_topbar_pin", use_container_width=True, help="Pin conversation"):
            st.toast("Conversation pinned to top!", icon="📌")

    with c_share:
        if st.button("🔗 Share", key="btn_topbar_share", use_container_width=True, help="Share conversation"):
            st.toast("Conversation link copied to clipboard!", icon="🔗")

    with c_clear:
        if st.button("🧹 Clear", key="btn_topbar_clear", use_container_width=True, help="Clear active conversation"):
            cid = st.session_state.get("conversation_id")
            if cid:
                api_client.delete_conversation(cid)
            st.session_state["conversation_id"] = None
            st.session_state["messages"] = []
            st.rerun()

    st.markdown("<hr style='margin: 8px 0 16px 0; border: none; border-bottom: 1px solid #E2E8F0;'>", unsafe_allow_html=True)

def render_jivan_empty_hero():
    st.markdown(
        """
        <div class="jivan-hero-section">
            <div class="jivan-hero-bubble">💬</div>
            <div class="jivan-hero-heading">Ask a question</div>
            <div class="jivan-hero-subheading">
                I can help you find insights, analyze information, and draft content using your knowledge.
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    # 3 Suggestion Pills
    col1, col2, col3 = st.columns([1, 1, 1])
    with col1:
        if st.button("💻 Write Python Code (Claude AI)", key="pill_code", use_container_width=True):
            st.session_state["queued_prompt"] = "Write a complete Python script for an asynchronous data pipeline with rate limiting"
            st.rerun()
    with col2:
        if st.button("📊 Create Pitch Deck (Canva AI)", key="pill_slides", use_container_width=True):
            st.session_state["queued_prompt"] = "Create a 5-slide pitch deck presentation on Autonomous AI Agents"
            st.rerun()
    with col3:
        if st.button("🍌 Generate Art (Nano Banana AI)", key="pill_art", use_container_width=True):
            st.session_state["queued_prompt"] = "Generate an image of a majestic cybernetic lion in neon Tokyo"
            st.rerun()

def render_jivan_messages():
    messages = st.session_state.get("messages", [])

    if not messages:
        render_jivan_empty_hero()
        return

    # Date separator
    st.markdown(
        """
        <div class="jivan-date-divider">
            <span class="jivan-date-pill">Today</span>
        </div>
        """,
        unsafe_allow_html=True
    )

    conv_id = st.session_state.get("conversation_id", "")
    user_email = st.session_state.get("user_email", "shubham@jivan.ai")
    clean_email = user_email.strip()
    prefix = clean_email.split("@")[0] if "@" in clean_email else clean_email
    user_initials = prefix[:2].upper() if len(prefix) >= 2 else prefix.upper() or "ME"

    for idx, msg in enumerate(messages):
        role = msg.get("role", "user")
        content = msg.get("content", "")
        msg_id = msg.get("id") or f"msg_{idx}"
        timestamp = msg.get("timestamp") or datetime.now().strftime("%I:%M %p")

        if role == "user":
            safe_content = html.escape(content).replace("\n", "<br>")
            st.markdown(
                f"""
                <div class="jivan-user-row">
                    <div class="jivan-user-bubble">
                        <div>{safe_content}</div>
                        <div class="jivan-user-time">{timestamp}</div>
                    </div>
                    <div class="jivan-user-avatar">{user_initials}</div>
                </div>
                """,
                unsafe_allow_html=True
            )
        else:
            col_avatar, col_card = st.columns([0.06, 0.94])
            with col_avatar:
                st.markdown('<div class="jivan-ai-avatar">✦</div>', unsafe_allow_html=True)
            with col_card:
                with st.container(border=True):
                    # Check for Specialist Badge
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
                        badge_color = "#0D9488" if "Canva" in specialist else ("#7C3AED" if "Banana" in specialist else "#2563EB")
                        st.markdown(
                            f'<div style="background: rgba(13, 148, 136, 0.08); border-left: 3px solid {badge_color}; color: {badge_color}; padding: 3px 10px; border-radius: 4px; font-size: 0.78rem; font-weight: 600; margin-bottom: 8px; display: inline-block;">✦ {specialist}</div>',
                            unsafe_allow_html=True
                        )

                    st.markdown(content)

                    # Generated Files (Images, Presentations, PDFs)
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
                                st.image(img_src, caption=gen_file.get("caption", "Nano Banana AI Visual"), use_container_width=True)

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

                    # Audio Player
                    audio_b64 = msg.get("audio_base64")
                    if audio_b64:
                        st.audio(audio_b64, format="audio/mp3")

                    # Citations
                    if meta and isinstance(meta, dict):
                        citations = meta.get("citations", [])
                        if citations:
                            with st.expander(f"📑 Grounded Sources ({len(citations)})", expanded=False):
                                for c in citations:
                                    st.markdown(f"**Document**: `{c.get('document_name')}` (Chunk #{c.get('chunk_index')})")
                                    st.caption(f"*\"{c.get('content')}\"*")

                    # Assistant Message Footer Actions: Timestamp + Copy + Feedback
                    c_time, c_copy, c_like, c_dislike = st.columns([0.82, 0.06, 0.06, 0.06])
                    with c_time:
                        st.caption(f"Assistant • {timestamp}")
                    with c_copy:
                        if st.button("📋", key=f"copy_{msg_id}", help="Copy response"):
                            st.toast("Copied response to clipboard!", icon="📋")
                    with c_like:
                        if st.button("👍", key=f"like_{msg_id}", help="Helpful"):
                            api_client.submit_feedback(conv_id, msg_id, "like")
                            st.toast("Feedback recorded: Helpful", icon="👍")
                    with c_dislike:
                        if st.button("👎", key=f"dislike_{msg_id}", help="Not helpful"):
                            api_client.submit_feedback(conv_id, msg_id, "dislike")
                            st.toast("Feedback recorded: Not helpful", icon="👎")

        st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)
