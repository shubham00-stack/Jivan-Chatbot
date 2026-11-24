"""
JIVAN Right Panel (Sources & Details Drawer) - Google Gemini Edition
Features:
- Gemini Grounding Inspector & Metadata Details
- Tabbed selector: 'Sources' and 'Details'
- Indexed document cards with chunk counters and delete actions
- Conversation metadata (Owner, Model, Security, Visibility)
"""

import streamlit as st
from datetime import datetime
from frontend.utils.api_client import api_client

def render_jivan_inspector():
    with st.container(border=True):
        st.markdown(
            """
            <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 12px;">
                <span style="font-weight: 600; font-size: 1rem;">📑 Grounding & Details</span>
            </div>
            """,
            unsafe_allow_html=True
        )

        col_tab1, col_tab2 = st.columns(2)
        current_tab = st.session_state.get("inspector_active_tab", "Sources")

        with col_tab1:
            if st.button("Sources", key="tab_sources", use_container_width=True):
                st.session_state["inspector_active_tab"] = "Sources"
                st.rerun()

        with col_tab2:
            if st.button("Details", key="tab_details", use_container_width=True):
                st.session_state["inspector_active_tab"] = "Details"
                st.rerun()

        current_tab = st.session_state.get("inspector_active_tab", "Sources")

        if current_tab == "Sources":
            docs = api_client.list_documents()

            if docs:
                for d in docs[:6]:
                    name = d.get("document_name", "Document")
                    ext = name.rsplit(".", 1)[-1].lower() if "." in name else "pdf"
                    chunks = d.get("chunk_count", 1)

                    st.markdown(
                        f"""
                        <div style="background: rgba(0,0,0,0.02); border: 1px solid rgba(0,0,0,0.06); border-radius: 12px; padding: 10px 12px; margin-bottom: 8px; display: flex; align-items: center; justify-content: space-between;">
                            <div>
                                <div style="font-weight: 500; font-size: 0.88rem;">📄 {name}</div>
                                <div style="font-size: 0.74rem; color: #747775;">{ext.upper()} • {chunks} chunks indexed</div>
                            </div>
                            <span style="background: rgba(66, 133, 244, 0.12); color: #1A73E8; font-weight: 600; font-size: 0.72rem; padding: 2px 8px; border-radius: 10px;">{chunks} chunks</span>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )
            else:
                st.markdown(
                    """
                    <div style="background: rgba(0,0,0,0.02); border: 1px solid rgba(0,0,0,0.06); border-radius: 12px; padding: 10px 12px; margin-bottom: 8px;">
                        <div style="font-weight: 500; font-size: 0.88rem;">📕 Q2 Financial Report.pdf</div>
                        <div style="font-size: 0.74rem; color: #747775;">PDF • Page 12 • Grounded</div>
                    </div>
                    <div style="background: rgba(0,0,0,0.02); border: 1px solid rgba(0,0,0,0.06); border-radius: 12px; padding: 10px 12px; margin-bottom: 8px;">
                        <div style="font-weight: 500; font-size: 0.88rem;">📗 Enterprise Pipeline.xlsx</div>
                        <div style="font-size: 0.74rem; color: #747775;">XLSX • Updated 5/14 • Grounded</div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

            with st.expander("Manage all sources →", expanded=False):
                st.caption("Active Knowledge Base Sources:")
                all_docs = api_client.list_documents()
                if all_docs:
                    for d in all_docs:
                        c1, c2 = st.columns([0.8, 0.2])
                        c1.write(f"📄 **{d['document_name']}** ({d['chunk_count']} chunks)")
                        if c2.button("🗑️", key=f"del_insp_{d['id']}"):
                            api_client.delete_document(d["id"])
                            st.rerun()
                else:
                    st.caption("No custom documents uploaded yet. Use '📎 Attach' or Knowledge menu to add.")

        else:
            user_email = st.session_state.get("user_email", "shubham@jivan.ai")
            time_str = datetime.now().strftime("%I:%M %p")

            st.markdown(
                f"""
                <div style="display: flex; flex-direction: column; gap: 14px; margin-top: 10px;">
                    <div>
                        <div style="font-size: 0.72rem; text-transform: uppercase; color: #747775; font-weight: 600;">Account</div>
                        <div style="font-size: 0.88rem; font-weight: 500;">{user_email}</div>
                    </div>
                    <div>
                        <div style="font-size: 0.72rem; text-transform: uppercase; color: #747775; font-weight: 600;">Active Model</div>
                        <div style="font-size: 0.88rem; font-weight: 500; color: #1A73E8;">✦ JIVAN 2.0 Flash (Groq + Claude + Canva)</div>
                    </div>
                    <div>
                        <div style="font-size: 0.72rem; text-transform: uppercase; color: #747775; font-weight: 600;">Session Time</div>
                        <div style="font-size: 0.88rem; font-weight: 500;">Today {time_str}</div>
                    </div>
                    <div>
                        <div style="font-size: 0.72rem; text-transform: uppercase; color: #747775; font-weight: 600;">Data Privacy</div>
                        <div style="font-size: 0.88rem; font-weight: 500;">🔒 Private & Enterprise Encrypted</div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )
