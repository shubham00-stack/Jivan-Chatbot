"""
JIVAN Right Panel (Sources & Details Drawer)
Features:
- Single clean unified container (no empty orphaned box at top)
- Tabbed selector: 'Sources' and 'Details'
- Sources List: Document cards with file type badges (PDF, XLSX, DOCX) and citation counts
- Action link: 'View all sources →'
- Details List: Owner, Created timestamp, Model (QWEN-3.8-27B Groq), Visibility (Private)
"""

import streamlit as st
from datetime import datetime
from frontend.utils.api_client import api_client

def render_jivan_inspector():
    with st.container(border=True):
        # 1. Tab Selector (Sources vs Details)
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
            # Fetch active indexed documents or display grounded sources
            docs = api_client.list_documents()

            if docs:
                for d in docs[:5]:
                    name = d.get("document_name", "Document")
                    ext = name.rsplit(".", 1)[-1].lower() if "." in name else "pdf"
                    badge_class = "jivan-badge-pdf" if ext == "pdf" else "jivan-badge-docx"
                    icon = "📄" if ext == "pdf" else "📝"
                    chunks = d.get("chunk_count", 1)

                    st.markdown(
                        f"""
                        <div class="jivan-source-card">
                            <div class="jivan-doc-badge {badge_class}">{icon}</div>
                            <div class="jivan-source-meta">
                                <div class="jivan-source-title">{name}</div>
                                <div class="jivan-source-subtitle">{ext.upper()} • {chunks} chunks indexed</div>
                            </div>
                            <div class="jivan-citation-count">{chunks}</div>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )
            else:
                # Default reference cards from reference design
                st.markdown(
                    """
                    <div class="jivan-source-card">
                        <div class="jivan-doc-badge jivan-badge-pdf">📕</div>
                        <div class="jivan-source-meta">
                            <div class="jivan-source-title">Q2 Financial Report</div>
                            <div class="jivan-source-subtitle">PDF • Page 12</div>
                        </div>
                        <div class="jivan-citation-count">1</div>
                    </div>

                    <div class="jivan-source-card">
                        <div class="jivan-doc-badge jivan-badge-xlsx">📗</div>
                        <div class="jivan-source-meta">
                            <div class="jivan-source-title">Enterprise Pipeline</div>
                            <div class="jivan-source-subtitle">XLSX • Updated 5/14</div>
                        </div>
                        <div class="jivan-citation-count">2</div>
                    </div>

                    <div class="jivan-source-card">
                        <div class="jivan-doc-badge jivan-badge-docx">📘</div>
                        <div class="jivan-source-meta">
                            <div class="jivan-source-title">Partner Contributions</div>
                            <div class="jivan-source-subtitle">DOCX • Updated 5/10</div>
                        </div>
                        <div class="jivan-citation-count">1</div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

            # 'View all sources →' expander
            with st.expander("View all sources →", expanded=False):
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
                    st.caption("No custom documents uploaded yet. Use '📎 Attach Files' or Knowledge menu to add.")

        # 2. Details Section
        user_email = st.session_state.get("user_email", "shubham@jivan.ai")
        conv_id = st.session_state.get("conversation_id", "New Session")
        time_str = datetime.now().strftime("%I:%M %p")

        st.markdown(
            f"""
            <div class="jivan-details-group">
                <div class="jivan-detail-row">
                    <span class="jivan-detail-label">Owner</span>
                    <span class="jivan-detail-val">{user_email}</span>
                </div>
                <div class="jivan-detail-row">
                    <span class="jivan-detail-label">Created</span>
                    <span class="jivan-detail-val">Today {time_str}</span>
                </div>
                <div class="jivan-detail-row">
                    <span class="jivan-detail-label">AI Engine</span>
                    <span class="jivan-detail-val" style="color: #0D9488; font-weight: 600;">Claude • Canva • Banana</span>
                </div>
                <div class="jivan-detail-row">
                    <span class="jivan-detail-label">Visibility</span>
                    <span class="jivan-detail-val">🔒 Private</span>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )
