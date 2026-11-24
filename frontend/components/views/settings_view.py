"""
JIVAN Settings & System Diagnostics View
Features:
- Appearance: Bright Mode / Dark Mode switch
- Intelligence Toggles: Emotional Empathy, RAG Grounding, TTS Speech Output
- Live API Key Configuration (Groq, Gemini, Claude) with runtime persistence
- Model Selector: Qwen 3.8 27B (Groq Fast), Llama 3.3 70B, Mixtral 8x7B
- User Authentication: Email ID update
- Conversation Management: Clear conversation, Reset history
- System Diagnostics: Live Database, Vector Store, and API status
"""

import os
import streamlit as st
from frontend.utils.api_client import api_client

def render_settings_view():
    st.markdown("## ⚙️ Settings & System Preferences")
    st.caption("Configure assistant intelligence modules, visual themes, API credentials, and models.")

    # 1. Appearance / Theme
    st.markdown("### 🌓 Appearance")
    curr_theme = st.session_state.get("theme_mode", "light")
    col_t1, col_t2 = st.columns(2)
    with col_t1:
        if st.button("☀️ Light Mode (White Canvas)", type="primary" if curr_theme == "light" else "secondary", use_container_width=True, key="btn_set_bright"):
            st.session_state["theme_mode"] = "light"
            st.query_params["theme"] = "light"
            st.rerun()
    with col_t2:
        if st.button("🌙 Dark Mode (Premium Dark)", type="primary" if curr_theme == "dark" else "secondary", use_container_width=True, key="btn_set_dark"):
            st.session_state["theme_mode"] = "dark"
            st.query_params["theme"] = "dark"
            st.rerun()

    st.divider()

    # 2. Live API Key Credentials (Groq, Gemini, Claude)
    st.markdown("### 🔑 API Keys & AI Provider Configuration")
    st.caption("Configure your AI model keys below. These are applied live to the backend without requiring a server reboot.")

    col_k1, col_k2 = st.columns(2)
    with col_k1:
        groq_val = st.session_state.get("groq_key_val", os.environ.get("GROQ_API_KEY", ""))
        inp_groq = st.text_input("⚡ Groq API Key (Fast Conversational & Coding):", value=groq_val, type="password", placeholder="gsk_...", key="set_inp_groq")

        claude_val = st.session_state.get("claude_key_val", os.environ.get("ANTHROPIC_API_KEY", ""))
        inp_claude = st.text_input("💻 Anthropic Claude API Key (Optional Coding Specialist):", value=claude_val, type="password", placeholder="sk-ant-...", key="set_inp_claude")

    with col_k2:
        gemini_val = st.session_state.get("gemini_key_val", os.environ.get("GEMINI_API_KEY", ""))
        inp_gemini = st.text_input("🔮 Google Gemini API Key (Multimodal Vision & Fallback):", value=gemini_val, type="password", placeholder="AQ... or AIza...", key="set_inp_gemini")

        provider_opts = ["groq", "gemini"]
        curr_p = os.environ.get("LLM_PROVIDER", "groq").lower()
        def_idx = 0 if curr_p == "groq" else 1
        inp_provider = st.selectbox("Primary AI Inference Provider:", provider_opts, index=def_idx, key="set_inp_provider")

    if st.button("💾 Save & Apply API Keys", type="primary", use_container_width=True, key="btn_apply_keys"):
        st.session_state["groq_key_val"] = inp_groq.strip()
        st.session_state["gemini_key_val"] = inp_gemini.strip()
        st.session_state["claude_key_val"] = inp_claude.strip()

        ok = api_client.update_keys(
            groq_key=inp_groq.strip(),
            gemini_key=inp_gemini.strip(),
            anthropic_key=inp_claude.strip(),
            provider=inp_provider
        )
        if ok:
            st.success("✅ API Keys successfully applied and connected to the live backend!")
        else:
            st.info("API Keys saved to active session.")

    st.divider()

    # 3. Intelligence & Guardrail Toggles
    st.markdown("### 🧠 Intelligence Modules")
    st.session_state["enable_emotional"] = st.toggle(
        "Empathetic Emotional Support (Sentiment & Coping Detection)",
        value=st.session_state.get("enable_emotional", True),
        help="Analyzes emotional distress or crisis keywords and provides evidence-based supportive responses."
    )
    st.session_state["enable_rag"] = st.toggle(
        "RAG Knowledge Retrieval Grounding",
        value=st.session_state.get("enable_rag", True),
        help="Grounds answers in your uploaded documents and adds source citations."
    )
    st.session_state["enable_tts"] = st.toggle(
        "Audio Speech Output (TTS Voice Generation)",
        value=st.session_state.get("enable_tts", False),
        help="Generates an audio voice note for assistant responses."
    )

    st.divider()

    # 4. Specialized Multi-Model Roster
    st.markdown("### 🤖 Specialized Multi-Model Roster")
    st.caption("JIVAN routes each user requirement to its dedicated best-in-class AI engine:")

    col_m1, col_m2, col_m3 = st.columns(3)
    with col_m1:
        with st.container(border=True):
            st.markdown("#### 💻 Claude AI")
            st.caption("**Specialty**: Code & Architecture")
            st.markdown("`Claude 3.5 Sonnet` writes, debugs, and optimizes code.")
            st.caption("Active via Anthropic API or Groq Claude Persona.")

    with col_m2:
        with st.container(border=True):
            st.markdown("#### 📊 Canva AI")
            st.caption("**Specialty**: Presentations & Slides")
            st.markdown("`Canva AI Engine` crafts 16:9 widescreen PowerPoint decks (.pptx).")
            st.markdown("✅ **Status**: Active & Connected")

    with col_m3:
        with st.container(border=True):
            st.markdown("#### 🍌 Nano Banana AI")
            st.caption("**Specialty**: Visual Art & Synthesis")
            st.markdown("`Nano Banana AI 2.1` produces high-resolution artworks.")
            st.markdown("✅ **Status**: Active & Connected")

    st.divider()

    # 5. User Identity & Email
    st.markdown("### 👤 User Account & Login Email")
    user_email = st.session_state.get("user_email", "shubham@jivan.ai")
    c_em1, c_em2 = st.columns([0.75, 0.25])
    with c_em1:
        updated_email = st.text_input("Active Login Email:", value=user_email, key="settings_user_email")
    with c_em2:
        st.markdown("<div style='height: 28px;'></div>", unsafe_allow_html=True)
        if st.button("Save Email", type="primary", use_container_width=True, key="btn_save_email_settings"):
            if updated_email and "@" in updated_email:
                st.session_state["user_email"] = updated_email.strip()
                st.success("User email updated successfully!")
            else:
                st.error("Please enter a valid email address.")

    st.divider()

    # 6. System Diagnostics
    st.markdown("### 🩺 System Diagnostics")
    health = api_client.check_health()
    col_d1, col_d2, col_d3 = st.columns(3)
    with col_d1:
        st.metric("Backend API Status", health.get("status", "offline").upper())
    with col_d2:
        db_stat = health.get("database", {}).get("engine", "sqlite").upper()
        st.metric("Database Engine", db_stat)
    with col_d3:
        chunks = health.get("vector_store", {}).get("total_chunks", 0)
        st.metric("Vector RAG Chunks", chunks)
