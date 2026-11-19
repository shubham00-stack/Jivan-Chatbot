import os
import json
import base64
import streamlit as st
from frontend.utils.api_client import api_client

def render_chat_view():
    messages = st.session_state.get("messages", [])

    if not messages:
        st.markdown(
            """
            <div style="text-align: center; padding: 40px 20px; border-radius: 12px; background: rgba(120, 120, 120, 0.08); margin-bottom: 25px;">
                <h2>🌟 Welcome to Multimodal AI Assistant</h2>
                <p style="font-size: 1.1em; color: #888;">
                    I can converse naturally, ground answers in your uploaded documents (RAG), 
                    analyze uploaded images, transcribe audio voice notes, and offer personal emotional support.
                </p>
                <div style="display: flex; justify-content: center; gap: 15px; margin-top: 20px; flex-wrap: wrap;">
                    <span style="background: rgba(33, 150, 243, 0.15); padding: 6px 14px; border-radius: 20px; font-size: 0.9em;">💬 Natural Conversation</span>
                    <span style="background: rgba(76, 175, 80, 0.15); padding: 6px 14px; border-radius: 20px; font-size: 0.9em;">📚 Document RAG</span>
                    <span style="background: rgba(255, 152, 0, 0.15); padding: 6px 14px; border-radius: 20px; font-size: 0.9em;">🖼️ Vision Intelligence</span>
                    <span style="background: rgba(156, 39, 176, 0.15); padding: 6px 14px; border-radius: 20px; font-size: 0.9em;">🎙️ Speech to Text</span>
                    <span style="background: rgba(233, 30, 99, 0.15); padding: 6px 14px; border-radius: 20px; font-size: 0.9em;">💖 Emotional Support</span>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )
        return

    # Render Messages
    for msg in messages:
        role = msg.get("role", "user")
        content = msg.get("content", "")
        avatar = "👤" if role == "user" else "🤖"

        with st.chat_message(role, avatar=avatar):
            st.markdown(content)

            # Metadata & Citations
            meta = msg.get("metadata")
            if isinstance(meta, str):
                try:
                    meta = json.loads(meta)
                except Exception:
                    meta = None

            if meta and isinstance(meta, dict):
                citations = meta.get("citations", [])
                if citations:
                    with st.expander(f"📖 Grounded Document Sources ({len(citations)})"):
                        for c in citations:
                            st.markdown(f"**Document**: `{c.get('document_name')}` (Chunk #{c.get('chunk_index')})")
                            st.caption(f"*\"{c.get('content')}\"*")
                            st.divider()

            # Audio Player if TTS audio was generated
            audio_base64 = msg.get("audio_base64")
            if audio_base64:
                st.audio(audio_base64, format="audio/mp3")

            # Render Generated Files (AI Images or PDFs)
            gen_file = msg.get("generated_file")
            if not gen_file and meta and isinstance(meta, dict):
                gen_file = meta.get("generated_file")

            if gen_file and isinstance(gen_file, dict):
                if gen_file.get("type") == "image":
                    img_src = gen_file.get("data_uri")
                    if not img_src and gen_file.get("file_path") and os.path.exists(gen_file["file_path"]):
                        img_src = gen_file["file_path"]
                    if img_src:
                        st.image(img_src, caption=gen_file.get("caption", "Generated Image"), use_container_width=True)
                elif gen_file.get("type") == "pdf":
                    raw_b64 = gen_file.get("file_bytes_b64")
                    pdf_bytes = None
                    if raw_b64:
                        pdf_bytes = base64.b64decode(raw_b64)
                    elif gen_file.get("file_path") and os.path.exists(gen_file["file_path"]):
                        with open(gen_file["file_path"], "rb") as f:
                            pdf_bytes = f.read()

                    if pdf_bytes:
                        st.download_button(
                            label=f"📥 Download {gen_file.get('filename', 'document.pdf')}",
                            data=pdf_bytes,
                            file_name=gen_file.get("filename", "document.pdf"),
                            mime="application/pdf",
                            key=f"dl_pdf_{msg.get('id', '')}_{gen_file.get('filename')}"
                        )

            # Feedback for assistant responses
            if role == "assistant" and msg.get("id"):
                msg_id = msg["id"]
                conv_id = st.session_state.get("conversation_id", "")
                f_col1, f_col2, _ = st.columns([0.08, 0.08, 0.84])
                if f_col1.button("👍", key=f"thumb_up_{msg_id}"):
                    api_client.submit_feedback(conv_id, msg_id, "like")
                    st.toast("Thank you for your feedback!", icon="👍")
                if f_col2.button("👎", key=f"thumb_down_{msg_id}"):
                    api_client.submit_feedback(conv_id, msg_id, "dislike")
                    st.toast("Thank you for your feedback!", icon="👎")

