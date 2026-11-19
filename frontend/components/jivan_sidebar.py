"""
JIVAN Left Sidebar Component
Features:
- Leaf badge & J I V A N branding
- '+ New conversation' Teal button
- Interactive Navigation: Conversations, Knowledge, Tasks, Templates, Settings
- Appearance: Bright Mode / Dark Mode Theme Switcher
- Filtered Recent Sessions based on active user email
- Working User Email Login card in bottom-left corner (no broken popover ligature words)
"""

import streamlit as st
from frontend.utils.api_client import api_client

def render_jivan_sidebar():
    with st.sidebar:
        # 1. JIVAN Branding Header
        st.markdown(
            """
            <div class="jivan-brand-wrapper">
                <div class="jivan-logo-badge">🍃</div>
                <div class="jivan-brand-title">JIVAN</div>
            </div>
            """,
            unsafe_allow_html=True
        )

        # 2. '+ New conversation' Action Button
        if st.button("➕ New conversation", key="jivan_btn_new_chat", type="primary", use_container_width=True):
            st.session_state["active_nav"] = "Conversations"
            st.session_state["conversation_id"] = None
            st.session_state["messages"] = []
            st.rerun()

        # 3. Sidebar Navigation Menu
        active_nav = st.session_state.get("active_nav", "Conversations")

        nav_items = [
            ("Conversations", "💬 Conversations"),
            ("Knowledge", "📖 Knowledge"),
            ("Tasks", "☑️ Tasks"),
            ("Templates", "📄 Templates"),
            ("Settings", "⚙️ Settings")
        ]

        for nav_key, nav_label in nav_items:
            is_active = (active_nav == nav_key)
            btn_text = f"➤ {nav_label}" if is_active else nav_label
            if st.button(
                btn_text,
                key=f"nav_{nav_key.lower()}",
                use_container_width=True
            ):
                st.session_state["active_nav"] = nav_key
                st.rerun()

        # 4. Dark Mode / Bright Mode Theme Toggle
        st.markdown('<div class="jivan-section-label">Appearance</div>', unsafe_allow_html=True)
        col_theme1, col_theme2 = st.columns(2)
        with col_theme1:
            if st.button("☀️ Bright", key="btn_theme_bright", use_container_width=True):
                st.session_state["theme_mode"] = "bright"
                st.rerun()
        with col_theme2:
            if st.button("🌙 Dark", key="btn_theme_dark", use_container_width=True):
                st.session_state["theme_mode"] = "dark"
                st.rerun()

        # 5. Recent Conversations (Filtered for logged-in user email)
        user_email = st.session_state.get("user_email", "shubham@jivan.ai")
        st.markdown('<div class="jivan-section-label">Recent Chats</div>', unsafe_allow_html=True)

        conversations = api_client.list_conversations(user_email=user_email)
        curr_id = st.session_state.get("conversation_id")

        if conversations:
            for conv in conversations[:7]:
                cid = conv.get("id")
                title = conv.get("conversation_title") or "Untitled Conversation"
                is_active = (cid == curr_id)

                col_btn, col_del = st.columns([0.82, 0.18])
                with col_btn:
                    display_title = (title[:20] + "...") if len(title) > 20 else title
                    btn_label = f"• {display_title}" if is_active else display_title
                    if st.button(btn_label, key=f"jivan_conv_{cid}", use_container_width=True, help=title):
                        st.session_state["active_nav"] = "Conversations"
                        st.session_state["conversation_id"] = cid
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
                        st.rerun()
        else:
            st.caption(f"No chats for {user_email[:18]} yet.")

        # 6. Real Working Email Login in Bottom-Left Corner (Zero Popovers / Zero Ligatures)
        st.markdown('<div style="margin-top: 15px;"></div>', unsafe_allow_html=True)

        clean_email = user_email.strip()
        prefix = clean_email.split("@")[0] if "@" in clean_email else clean_email
        initials = prefix[:2].upper() if len(prefix) >= 2 else prefix.upper() or "ME"

        col_prof, col_edit = st.columns([0.80, 0.20])
        with col_prof:
            st.markdown(
                f"""
                <div class="jivan-profile-card">
                    <div class="jivan-profile-avatar">{initials}</div>
                    <div class="jivan-profile-info">
                        <div class="jivan-profile-name">{clean_email}</div>
                        <div class="jivan-profile-role">Active Account • Verified</div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )
        with col_edit:
            st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)
            if st.button("✏️", key="btn_toggle_email_edit", help="Login / Change Email ID"):
                st.session_state["show_email_drawer"] = not st.session_state.get("show_email_drawer", False)
                st.rerun()

        # Email Login Drawer
        if st.session_state.get("show_email_drawer"):
            with st.container(border=True):
                st.markdown("##### 🔑 Login / Switch Account")
                new_email = st.text_input("Enter Email ID:", value=user_email, key="sidebar_new_email_val")
                col_s1, col_s2 = st.columns(2)
                with col_s1:
                    if st.button("Save", type="primary", use_container_width=True, key="btn_save_email_sidebar"):
                        if new_email and "@" in new_email:
                            st.session_state["user_email"] = new_email.strip()
                            st.session_state["show_email_drawer"] = False
                            st.rerun()
                        else:
                            st.error("Please enter a valid email.")
                with col_s2:
                    if st.button("Close", use_container_width=True, key="btn_close_email_sidebar"):
                        st.session_state["show_email_drawer"] = False
                        st.rerun()
