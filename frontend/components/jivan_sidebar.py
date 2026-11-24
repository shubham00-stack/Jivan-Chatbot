"""
JIVAN Left Sidebar Component - Google Gemini Edition
Features:
- Gemini Iridescent Sparkle Logo ✦ and JIVAN Branding with '2.0 Flash' badge
- '+ New chat' Gemini Capsule Pill button
- Gemini Navigation Menu (Chat, Knowledge Base, Tasks, Prompts, Settings)
- Appearance Switcher (☀️ Light / 🌙 Dark)
- Filtered Recent Chats list with instant switching & delete
- Bottom Google Account-style Profile Pill for active user email
"""

import streamlit as st
from frontend.utils.api_client import api_client

def render_jivan_sidebar():
    with st.sidebar:
        # 1. Gemini Brand Header with Sparkle Logo
        st.markdown(
            """
            <div class="gemini-brand-wrapper">
                <div class="gemini-sparkle-logo">✦</div>
                <div class="gemini-brand-title">
                    <span>JIVAN</span>
                    <span class="gemini-brand-badge">2.0 Flash</span>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

        # 2. '+ New chat' Gemini Pill Button
        if st.button("➕ New chat", key="jivan_btn_new_chat", use_container_width=True):
            st.session_state["active_nav"] = "Conversations"
            st.session_state["conversation_id"] = None
            st.session_state["messages"] = []
            st.session_state["conversation_title"] = "New Chat"
            st.rerun()

        st.markdown("<div style='height: 8px;'></div>", unsafe_allow_html=True)

        # 3. Gemini Navigation Menu
        active_nav = st.session_state.get("active_nav", "Conversations")

        nav_items = [
            ("Conversations", "💬 Chat"),
            ("Knowledge", "💎 Knowledge Base"),
            ("Tasks", "☑️ Tasks"),
            ("Templates", "📄 Prompts"),
            ("Settings", "⚙️ Settings")
        ]

        for nav_key, nav_label in nav_items:
            is_active = (active_nav == nav_key)
            display_label = f"● {nav_label}" if is_active else nav_label
            if st.button(
                display_label,
                key=f"nav_{nav_key.lower()}",
                use_container_width=True
            ):
                st.session_state["active_nav"] = nav_key
                st.rerun()

        # 4. Appearance Mode (☀️ Light / 🌙 Dark)
        st.markdown('<div class="gemini-sidebar-heading">Theme</div>', unsafe_allow_html=True)
        col_t1, col_t2 = st.columns(2)
        curr_theme = st.session_state.get("theme_mode", "light")
        with col_t1:
            if st.button("☀️ Light", key="btn_theme_bright", use_container_width=True, type="primary" if curr_theme == "light" else "secondary"):
                st.session_state["theme_mode"] = "light"
                st.query_params["theme"] = "light"
                st.rerun()
        with col_t2:
            if st.button("🌙 Dark", key="btn_theme_dark", use_container_width=True, type="primary" if curr_theme == "dark" else "secondary"):
                st.session_state["theme_mode"] = "dark"
                st.query_params["theme"] = "dark"
                st.rerun()

        # 5. Recent Chats (Filtered by logged-in user email)
        st.markdown('<div class="gemini-sidebar-heading">Recent</div>', unsafe_allow_html=True)
        user_email = st.session_state.get("user_email", "shubham@jivan.ai")
        conversations = api_client.list_conversations(user_email=user_email)
        curr_id = st.session_state.get("conversation_id")

        if conversations:
            for conv in conversations[:8]:
                cid = conv.get("id")
                title = conv.get("conversation_title") or "Untitled Conversation"
                is_active = (cid == curr_id)

                col_btn, col_del = st.columns([0.84, 0.16])
                with col_btn:
                    display_title = (title[:22] + "...") if len(title) > 22 else title
                    btn_text = f"💬 {display_title}" if not is_active else f"✦ {display_title}"
                    if st.button(btn_text, key=f"jivan_conv_{cid}", use_container_width=True, help=title):
                        st.session_state["active_nav"] = "Conversations"
                        st.session_state["conversation_id"] = cid
                        st.session_state["conversation_title"] = title
                        detail = api_client.get_conversation(cid)
                        if detail and "messages" in detail:
                            st.session_state["messages"] = [
                                {
                                    "id": m["id"],
                                    "role": m["message_role"],
                                    "content": m["message_content"],
                                    "modality": m.get("modality", "text"),
                                    "metadata": m.get("metadata_json")
                                }
                                for m in detail["messages"]
                            ]
                        st.rerun()

                with col_del:
                    if st.button("✕", key=f"jivan_del_{cid}", help="Delete chat"):
                        api_client.delete_conversation(cid)
                        if st.session_state.get("conversation_id") == cid:
                            st.session_state["conversation_id"] = None
                            st.session_state["messages"] = []
                            st.session_state["conversation_title"] = "New Chat"
                        st.rerun()
        else:
            st.caption("No recent conversations yet.")

        # 6. Google Account-Style User Profile Pill
        st.markdown('<div style="margin-top: 20px;"></div>', unsafe_allow_html=True)
        clean_email = user_email.strip()
        prefix = clean_email.split("@")[0] if "@" in clean_email else clean_email
        initials = prefix[:2].upper() if len(prefix) >= 2 else prefix.upper() or "SH"

        col_prof, col_edit = st.columns([0.82, 0.18])
        with col_prof:
            st.markdown(
                f"""
                <div class="gemini-profile-pill">
                    <div class="gemini-avatar-circle">{initials}</div>
                    <div class="gemini-profile-text">
                        <div class="gemini-profile-email">{clean_email}</div>
                        <div class="gemini-profile-status">Active Account</div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )
        with col_edit:
            st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)
            if st.button("✏️", key="btn_toggle_email_edit", help="Switch / Edit Account Email"):
                st.session_state["show_email_drawer"] = not st.session_state.get("show_email_drawer", False)
                st.rerun()

        # Account Switch Drawer
        if st.session_state.get("show_email_drawer"):
            with st.container(border=True):
                st.markdown("###### 👤 Switch User Account")
                new_email = st.text_input("Enter Email ID:", value=user_email, key="sidebar_new_email_val")
                col_s1, col_s2 = st.columns(2)
                with col_s1:
                    if st.button("Save", type="primary", use_container_width=True, key="btn_save_email_sidebar"):
                        if new_email and "@" in new_email:
                            st.session_state["user_email"] = new_email.strip()
                            st.session_state["show_email_drawer"] = False
                            st.rerun()
                        else:
                            st.error("Enter valid email.")
                with col_s2:
                    if st.button("Close", use_container_width=True, key="btn_close_email_sidebar"):
                        st.session_state["show_email_drawer"] = False
                        st.rerun()
