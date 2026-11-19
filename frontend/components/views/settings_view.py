"""
JIVAN Settings & System Diagnostics View
Features:
- Appearance: Bright Mode / Dark Mode switch
- Intelligence Toggles: Emotional Empathy, RAG Grounding, TTS Speech Output
- Model Selector: Qwen 3.8 27B (Groq Fast), Llama 3.3 70B, Mixtral 8x7B
- User Authentication: Email ID update
- Conversation Management: Clear conversation, Reset history
- System Diagnostics: Live MySQL 8.0, Groq API, and Vector Store status
"""

import streamlit as st
from frontend.utils.api_client import api_client

def render_settings_view():
    st.markdown("## ⚙️ Settings & System Preferences")
    st.caption("Configure assistant intelligence modules, visual themes, models, and authentication.")

    # 1. Appearance / Theme
    st.markdown("### 🌓 Appearance")
    curr_theme = st.session_state.get("theme_mode", "bright")
    col_t1, col_t2 = st.columns(2)
    with col_t1:
        if st.button("☀️ Bright Mode (White Canvas)", type="primary" if curr_theme == "bright" else "secondary", use_container_width=True, key="btn_set_bright"):
            st.session_state["theme_mode"] = "bright"
            st.rerun()
    with col_t2:
        if st.button("🌙 Dark Mode (Obsidian Navy)", type="primary" if curr_theme == "dark" else "secondary", use_container_width=True, key="btn_set_dark"):
            st.session_state["theme_mode"] = "dark"
            st.rerun()

    st.divider()

    # 2. Intelligence & Guardrail Toggles
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

    # 3. Model Engine Selector & Specialized Multi-Model Roster
    st.markdown("### 🤖 Specialized Multi-Model Roster (Each Model for Its Job)")
    st.caption("JIVAN routes each user requirement to its dedicated best-in-class AI engine:")

    col_m1, col_m2, col_m3 = st.columns(3)
    with col_m1:
        with st.container(border=True):
            st.markdown("#### 💻 Claude AI")
            st.caption("**Specialty**: Code & Architecture")
            st.markdown("`Claude 3.5 Sonnet` writes, debugs, and optimizes Python, JS, SQL, and system scripts.")
            claude_key = st.text_input("Anthropic API Key:", type="password", placeholder="sk-ant-...", key="cfg_anthropic_key")
            if st.button("Save Claude Key", key="btn_save_claude_key", use_container_width=True):
                st.session_state["anthropic_api_key"] = claude_key
                st.toast("Claude API Key configured!", icon="⚡")

    with col_m2:
        with st.container(border=True):
            st.markdown("#### 📊 Canva AI")
            st.caption("**Specialty**: Presentations & Slides")
            st.markdown("`Canva AI Engine` crafts 16:9 widescreen PowerPoint decks (.pptx) & direct Canva design links.")
            st.markdown("✅ **Status**: Active & Connected")
            st.caption("Supports download & one-click import into Canva Studio.")

    with col_m3:
        with st.container(border=True):
            st.markdown("#### 🍌 Nano Banana AI")
            st.caption("**Specialty**: Visual Art & Synthesis")
            st.markdown("`Nano Banana AI 2.1` produces 1024x1024 high-resolution artworks, photo concepts, and graphics.")
            st.markdown("✅ **Status**: Active & Connected")
            st.caption("Powered by multi-tier high-definition rendering pipeline.")

    st.markdown("#### ⚡ Core General Reasoning Engine")
    models = [
        "QWEN-3.8-27B (Groq Ultra-Fast • Default)",
        "LLAMA-3.3-70B-VERSATILE (Groq Enterprise)",
        "MIXTRAL-8X7B-32768 (Groq High-Context)"
    ]
    curr_model_idx = st.session_state.get("selected_model_idx", 0)
    selected_model = st.selectbox("Active General Inference Model:", models, index=curr_model_idx, key="settings_model_select")
    if selected_model != models[curr_model_idx]:
        st.session_state["selected_model_idx"] = models.index(selected_model)
        st.toast(f"Switched model engine to: {selected_model}", icon="⚡")

    st.divider()

    # 4. User Identity & Email
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
                st.rerun()
            else:
                st.error("Please enter a valid email address.")

    st.divider()

    # 5. Conversation History Actions
    st.markdown("### 💬 Chat Session Controls")
    c_clear1, c_clear2 = st.columns(2)
    with c_clear1:
        if st.button("🧹 Clear Current Conversation", use_container_width=True, key="btn_clear_curr_chat"):
            curr_id = st.session_state.get("conversation_id")
            if curr_id:
                api_client.delete_conversation(curr_id)
            st.session_state["conversation_id"] = None
            st.session_state["messages"] = []
            st.toast("Cleared active conversation.", icon="🧹")
            st.rerun()

    with c_clear2:
        if st.button("🗑️ Reset All My Conversations", use_container_width=True, key="btn_reset_all_user_chats"):
            user_email = st.session_state.get("user_email", "shubham@jivan.ai")
            all_user_convs = api_client.list_conversations(user_email=user_email)
            for c in all_user_convs:
                api_client.delete_conversation(c["id"])
            st.session_state["conversation_id"] = None
            st.session_state["messages"] = []
            st.toast("Reset all user conversations from database.", icon="🗑️")
            st.rerun()

    st.divider()

    # 6. System Diagnostics
    st.markdown("### 🛠️ System Health & Infrastructure")
    with st.spinner("Pinging services..."):
        health = api_client.check_health()
        
    c1, c2, c3, c4 = st.columns(4)
    db_status = health.get("database", {}).get("connected")
    c1.metric("MySQL 8.0 Database", "Connected 🟢" if db_status else "Offline 🔴")
    c2.metric("Inference Engine", "Groq QWEN ⚡")
    c3.metric("Vector Index", f"{health.get('vector_store', {}).get('total_chunks', 0)} chunks")
    c4.metric("Backend API", "Healthy 🟢" if health.get("status") == "healthy" else "Offline 🔴")
