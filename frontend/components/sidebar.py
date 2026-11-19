import streamlit as st
from frontend.utils.api_client import api_client

def render_sidebar():
    with st.sidebar:
        st.title("🤖 Navigation & Settings")

        # 1. New Conversation Button
        if st.button("➕ New Conversation", use_container_width=True, type="primary"):
            st.session_state["conversation_id"] = None
            st.session_state["messages"] = []
            st.rerun()

        st.divider()

        # 2. Conversation History
        st.subheader("💬 Recent Conversations")
        conversations = api_client.list_conversations()
        if conversations:
            for conv in conversations:
                col1, col2 = st.columns([0.8, 0.2])
                title = conv.get("conversation_title", "Untitled")
                cid = conv.get("id")
                is_current = (st.session_state.get("conversation_id") == cid)
                
                label = f"👉 {title[:20]}" if is_current else f"🗨️ {title[:20]}"
                if col1.button(label, key=f"conv_{cid}", use_container_width=True):
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

                if col2.button("🗑️", key=f"del_{cid}"):
                    api_client.delete_conversation(cid)
                    if st.session_state.get("conversation_id") == cid:
                        st.session_state["conversation_id"] = None
                        st.session_state["messages"] = []
                    st.rerun()
        else:
            st.caption("No conversations yet.")

        # Clear Current Conversation
        if st.session_state.get("conversation_id"):
            if st.button("🧹 Clear This Conversation", use_container_width=True):
                cid = st.session_state["conversation_id"]
                api_client.delete_conversation(cid)
                st.session_state["conversation_id"] = None
                st.session_state["messages"] = []
                st.rerun()

        st.divider()

        # 3. Knowledge Base Documents Manager
        st.subheader("📚 Knowledge Base (RAG)")
        uploaded_docs = st.file_uploader("Upload PDF or TXT Files", type=["pdf", "txt"], accept_multiple_files=True, key="kb_doc_uploader")
        if uploaded_docs:
            if st.button(f"📥 Index {len(uploaded_docs)} Document(s)", use_container_width=True):
                with st.spinner(f"Parsing, chunking, and indexing {len(uploaded_docs)} document(s)..."):
                    try:
                        file_payload = [(doc.name, doc.getvalue()) for doc in uploaded_docs]
                        results = api_client.upload_multiple_documents(file_payload)
                        success_count = sum(1 for r in results if r.get("success"))
                        st.success(f"Successfully indexed {success_count} of {len(uploaded_docs)} file(s)!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Upload failed: {e}")

        # List indexed documents
        docs = api_client.list_documents()
        if docs:
            st.caption(f"**{len(docs)} Indexed Documents:**")
            for d in docs:
                c1, c2 = st.columns([0.8, 0.2])
                c1.write(f"📄 **{d['document_name'][:18]}** ({d['chunk_count']} chunks)")
                if c2.button("❌", key=f"deldoc_{d['id']}"):
                    api_client.delete_document(d["id"])
                    st.rerun()
        else:
            st.caption("No knowledge documents indexed.")

        st.divider()

        # 4. Settings & Feature Toggles
        st.subheader("⚙️ Settings")
        st.session_state["enable_emotional"] = st.checkbox(
            "Empathetic Emotional Support",
            value=st.session_state.get("enable_emotional", True)
        )
        st.session_state["enable_rag"] = st.checkbox(
            "RAG Knowledge Retrieval",
            value=st.session_state.get("enable_rag", True)
        )
        st.session_state["enable_tts"] = st.checkbox(
            "Voice Speech Audio (TTS)",
            value=st.session_state.get("enable_tts", False)
        )

        st.divider()

        # 5. System Health Status
        health = api_client.check_health()
        status_color = "🟢" if health.get("status") == "healthy" else "🔴"
        st.caption(f"**System Status**: {status_color} {health.get('status', 'unknown').capitalize()}")
        if health.get("status") == "healthy":
            db_engine = health.get("database", {}).get("engine", "N/A")
            chunks_total = health.get("vector_store", {}).get("total_chunks", 0)
            st.caption(f"• DB: `{db_engine.upper()}` | Vectors: `{chunks_total}` chunks")

