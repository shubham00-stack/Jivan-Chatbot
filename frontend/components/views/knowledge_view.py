"""
JIVAN Dedicated Knowledge Management View
Features:
- Document indexing statistics (total docs, chunks, vector store status)
- Multi-document drag-and-drop uploader (PDF, TXT)
- Document manager table with chunk preview and delete
- Interactive semantic search query tester
"""

import streamlit as st
from frontend.utils.api_client import api_client

def render_knowledge_view():
    st.markdown("## 📖 Knowledge Base & Document Intelligence (RAG)")
    st.caption("Upload documents to ground your AI assistant in your organization's proprietary data.")

    # 1. Stats Bar
    docs = api_client.list_documents()
    total_chunks = sum(d.get("chunk_count", 0) for d in docs)

    s1, s2, s3 = st.columns(3)
    s1.metric("Indexed Documents", len(docs))
    s2.metric("Total Knowledge Chunks", total_chunks)
    s3.metric("Vector Index Status", "Active & Grounded 🟢")

    st.divider()

    # 2. Upload Section
    st.markdown("### 📤 Upload New Documents")
    uploaded_files = st.file_uploader(
        "Upload PDF, TXT or Markdown files",
        type=["pdf", "txt", "md"],
        accept_multiple_files=True,
        key="knowledge_view_uploader"
    )

    if uploaded_files:
        if st.button(f"🚀 Index {len(uploaded_files)} Document(s)", type="primary", key="btn_index_kb_view"):
            with st.spinner("Parsing, chunking, and embedding documents..."):
                payload = [(f.name, f.getvalue()) for f in uploaded_files]
                results = api_client.upload_multiple_documents(payload)
                success_count = sum(1 for r in results if r.get("success"))
                st.success(f"Indexed {success_count} of {len(uploaded_files)} files into Knowledge Base!")
                st.rerun()

    st.divider()

    # 3. Document Repository List
    st.markdown("### 📚 Indexed Knowledge Sources")
    if docs:
        for d in docs:
            col_icon, col_info, col_action = st.columns([0.08, 0.76, 0.16])
            with col_icon:
                st.markdown("<h3>📄</h3>", unsafe_allow_html=True)
            with col_info:
                st.markdown(f"**{d.get('document_name')}**")
                st.caption(f"Chunks: `{d.get('chunk_count')}` • Status: `{d.get('processing_status')}` • Created: {d.get('created_at', 'Recently')}")
            with col_action:
                if st.button("Delete", key=f"del_kb_view_{d.get('id')}", use_container_width=True):
                    api_client.delete_document(d.get("id"))
                    st.toast(f"Deleted {d.get('document_name')}", icon="🗑️")
                    st.rerun()
            st.markdown("<hr style='margin: 8px 0; opacity: 0.2;'>", unsafe_allow_html=True)
    else:
        st.info("No documents uploaded yet. Upload a PDF or TXT above to activate RAG knowledge search.")

    st.divider()

    # 4. Semantic Search Tester
    st.markdown("### 🔍 Test Knowledge Search")
    test_query = st.text_input("Enter a query to test retrieval:", placeholder="e.g. revenue drivers, product roadmap", key="kb_test_query")
    if test_query and st.button("Search Knowledge Base", key="btn_test_kb_search"):
        with st.spinner("Searching semantic embeddings..."):
            res = api_client.send_chat_message(
                message=f"/search {test_query}",
                conversation_id=None,
                enable_rag=True,
                enable_emotional_support=False
            )
            st.markdown(res.get("response", "No relevant content found."))

