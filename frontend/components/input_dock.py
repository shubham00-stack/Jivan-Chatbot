import streamlit as st
import base64
from frontend.utils.api_client import api_client

def render_input_dock():
    # CSS to ensure unrestricted paste and clean dock styling
    st.markdown(
        """
        <style>
        [data-testid="stChatInput"] textarea {
            user-select: text !important;
            -webkit-user-select: text !important;
        }
        .dock-toolbar {
            display: flex;
            align-items: center;
            gap: 10px;
            margin-bottom: 5px;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    # Toolbar row right above chat input: [📎 Add Files] [📋 Paste Text / Code] [Quick Command Pills]
    c_attach, c_paste, c_quick = st.columns([0.16, 0.22, 0.62])

    # 1. Multiple Files Attachment (Positioned on the Left)
    with c_attach:
        with st.popover("📎 Add Files", use_container_width=True, help="Attach multiple images, documents, or audio files"):
            st.markdown("#### 📎 Attach Multiple Files")
            attached_files = st.file_uploader(
                "Choose files (PDF, TXT, Images, Audio)",
                type=["png", "jpg", "jpeg", "webp", "pdf", "txt", "mp3", "wav", "m4a"],
                accept_multiple_files=True,
                key="dock_multi_uploader"
            )
            prompt_instruction = st.text_input(
                "Instruction for attached files (optional):",
                value="",
                placeholder="e.g. summarize these, or analyze this image",
                key="dock_files_prompt"
            )

            if attached_files and st.button(f"🚀 Upload & Process ({len(attached_files)} files)", type="primary", use_container_width=True):
                with st.spinner("Processing attached files..."):
                    # Categorize files
                    docs_to_index = []
                    images_to_process = []
                    audio_to_process = []

                    for f in attached_files:
                        ext = f.name.rsplit(".", 1)[-1].lower() if "." in f.name else ""
                        if ext in ("pdf", "txt"):
                            docs_to_index.append(f)
                        elif ext in ("png", "jpg", "jpeg", "webp"):
                            images_to_process.append(f)
                        elif ext in ("mp3", "wav", "m4a", "ogg"):
                            audio_to_process.append(f)

                    conv_id = st.session_state.get("conversation_id")

                    # Process documents
                    if docs_to_index:
                        file_payload = [(d.name, d.getvalue()) for d in docs_to_index]
                        results = api_client.upload_multiple_documents(file_payload)
                        succ = sum(1 for r in results if r.get("success"))
                        doc_names = ", ".join([d.name for d in docs_to_index])
                        st.session_state["messages"].append({
                            "role": "user",
                            "content": f"📎 Attached {len(docs_to_index)} document(s): `{doc_names}`" + (f"\n\n**Question**: {prompt_instruction}" if prompt_instruction else ""),
                            "modality": "document"
                        })

                        # If user asked a question, answer from indexed documents
                        query = prompt_instruction if prompt_instruction else f"Please summarize the main points of {doc_names}"
                        chat_res = api_client.send_chat_message(
                            message=query,
                            conversation_id=conv_id,
                            enable_emotional_support=False,
                            enable_rag=True,
                            enable_tts=st.session_state.get("enable_tts", False)
                        )
                        st.session_state["conversation_id"] = chat_res["conversation_id"]
                        st.session_state["messages"].append({
                            "id": chat_res["message_id"],
                            "role": "assistant",
                            "content": chat_res["response"],
                            "modality": "text",
                            "metadata": {"citations": chat_res.get("citations", [])}
                        })

                    # Process images
                    for img in images_to_process:
                        img_prompt = prompt_instruction or "Please analyze and describe this image in detail."
                        img_res = api_client.send_image_message(
                            file_bytes=img.getvalue(),
                            filename=img.name,
                            prompt=img_prompt,
                            conversation_id=conv_id
                        )
                        st.session_state["conversation_id"] = img_res["conversation_id"]
                        st.session_state["messages"].append({
                            "role": "user",
                            "content": f"[Uploaded Image: {img.name}] {img_prompt}",
                            "modality": "image"
                        })
                        st.session_state["messages"].append({
                            "id": img_res["message_id"],
                            "role": "assistant",
                            "content": img_res["response"],
                            "modality": "text"
                        })

                    # Process audio
                    for aud in audio_to_process:
                        aud_res = api_client.send_audio_message(
                            file_bytes=aud.getvalue(),
                            filename=aud.name,
                            conversation_id=conv_id,
                            enable_tts=st.session_state.get("enable_tts", False)
                        )
                        st.session_state["conversation_id"] = aud_res["conversation_id"]
                        st.session_state["messages"].append({
                            "role": "user",
                            "content": f"🎙️ *\"{aud_res['transcript']}\"*",
                            "modality": "audio"
                        })
                        st.session_state["messages"].append({
                            "id": aud_res["message_id"],
                            "role": "assistant",
                            "content": aud_res["response"],
                            "modality": "text",
                            "audio_base64": aud_res.get("audio_base64")
                        })

                    st.rerun()

    # 2. Paste Long External Text / Code Popover
    with c_paste:
        with st.popover("📋 Paste Text / Code", use_container_width=True, help="Paste long articles, documents, or code from other sources"):
            st.markdown("#### 📋 Paste External Content")
            pasted_content = st.text_area(
                "Paste your text, essay, or code here without formatting limits:",
                height=180,
                placeholder="Paste any article, code snippet, or notes here...",
                key="dock_pasted_text"
            )
            paste_action = st.radio(
                "Action for pasted text:",
                ["Ask AI / Analyze Content", "Save as Knowledge Document (TXT)"],
                horizontal=True,
                key="dock_paste_action"
            )
            if pasted_content and st.button("📤 Send Pasted Content", type="primary", use_container_width=True):
                if paste_action == "Save as Knowledge Document (TXT)":
                    with st.spinner("Indexing pasted text into knowledge base..."):
                        txt_bytes = pasted_content.encode("utf-8")
                        res = api_client.upload_document(txt_bytes, "pasted_note.txt")
                        st.toast(f"Indexed as knowledge document with {res.get('chunk_count', 1)} chunks!", icon="📚")
                        st.rerun()
                else:
                    # Send as conversational message
                    st.session_state["messages"].append({
                        "role": "user",
                        "content": pasted_content,
                        "modality": "text"
                    })
                    with st.spinner("Processing..."):
                        res = api_client.send_chat_message(
                            message=pasted_content,
                            conversation_id=st.session_state.get("conversation_id"),
                            enable_emotional_support=st.session_state.get("enable_emotional", True),
                            enable_rag=st.session_state.get("enable_rag", True),
                            enable_tts=st.session_state.get("enable_tts", False)
                        )
                        st.session_state["conversation_id"] = res["conversation_id"]
                        st.session_state["messages"].append({
                            "id": res["message_id"],
                            "role": "assistant",
                            "content": res["response"],
                            "modality": "text",
                            "generated_file": res.get("generated_file"),
                            "metadata": {"intent": res.get("intent"), "citations": res.get("citations", [])}
                        })
                        st.rerun()

    # 3. Quick Command Badges (Right side)
    with c_quick:
        st.caption("💡 Quick Commands: `/help` • `/image <prompt>` • `/pdf <topic>` • `/search <query>` • `/coping` • `/model`")

