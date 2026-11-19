"""
JIVAN Floating Composer Component
Features:
- Clean toggle-based action toolbar (no broken popover ligature words like 'expand_more')
- Multi-file attachment tray (PDF, TXT, images, audio) with instant processing
- Live microphone voice recording with Whisper transcription
- Quick action pills for /image, /pdf, and /coping
- Pure bright white card styling in bright mode
"""

import streamlit as st
from frontend.utils.api_client import api_client

def render_jivan_composer():
    # Toolbar Action Row (5 clean, high-visibility pill buttons)
    c1, c2, c3, c4, c5 = st.columns([0.20, 0.20, 0.20, 0.20, 0.20])

    with c1:
        attach_active = st.session_state.get("show_attach_tray", False)
        attach_label = "📎 Hide" if attach_active else "📎 Attach"
        if st.button(attach_label, key="btn_toggle_attach", use_container_width=True, help="Attach files (PDF, images, audio)"):
            st.session_state["show_attach_tray"] = not attach_active
            st.session_state["show_voice_tray"] = False
            st.rerun()

    with c2:
        voice_active = st.session_state.get("show_voice_tray", False)
        voice_label = "🎙️ Hide" if voice_active else "🎙️ Voice"
        if st.button(voice_label, key="btn_toggle_voice", use_container_width=True, help="Record audio voice note"):
            st.session_state["show_voice_tray"] = not voice_active
            st.session_state["show_attach_tray"] = False
            st.rerun()

    with c3:
        if st.button("🍌 /image", key="btn_quick_image", use_container_width=True, help="Nano Banana AI Visual Studio"):
            st.session_state["queued_prompt"] = "/image a futuristic cybernetic neon tiger in rainforest, 4k ultra detailed"
            st.rerun()

    with c4:
        if st.button("📊 /slides", key="btn_quick_slides", use_container_width=True, help="Canva AI Presentation Generator"):
            st.session_state["queued_prompt"] = "/presentation Next-Generation Autonomous AI Agents & Enterprise Architecture"
            st.rerun()

    with c5:
        if st.button("💻 /code", key="btn_quick_code", use_container_width=True, help="Claude 3.5 Sonnet Coding Specialist"):
            st.session_state["queued_prompt"] = "/code write an asynchronous web crawler with rate-limiting and retry logic in Python"
            st.rerun()

    # 1. Attachment Drawer (Shown when '📎 Attach Files' is toggled)
    if st.session_state.get("show_attach_tray"):
        with st.container(border=True):
            st.markdown("#### 📎 Attach Multiple Files")
            st.caption("Upload documents, images, or audio recordings to process in this conversation.")

            device_files = st.file_uploader(
                "Choose files (PDF, TXT, Images, Audio):",
                type=["pdf", "txt", "png", "jpg", "jpeg", "webp", "mp3", "wav", "m4a"],
                accept_multiple_files=True,
                key="jivan_multi_file_uploader_tray"
            )

            instruction = st.text_input(
                "Instruction for attached files (optional):",
                placeholder="e.g. summarize these documents, analyze chart",
                key="jivan_file_instruction_tray"
            )

            col_proc, col_close = st.columns([0.7, 0.3])
            with col_proc:
                if device_files and st.button(f"🚀 Upload & Process {len(device_files)} File(s)", type="primary", use_container_width=True, key="btn_proc_files_tray"):
                    with st.spinner("Processing attached files..."):
                        docs = [f for f in device_files if f.name.rsplit(".", 1)[-1].lower() in ("pdf", "txt", "md")]
                        imgs = [f for f in device_files if f.name.rsplit(".", 1)[-1].lower() in ("png", "jpg", "jpeg", "webp")]
                        audios = [f for f in device_files if f.name.rsplit(".", 1)[-1].lower() in ("mp3", "wav", "m4a")]

                        conv_id = st.session_state.get("conversation_id")
                        user_email = st.session_state.get("user_email", "shubham@jivan.ai")

                        # Process Documents
                        if docs:
                            payload = [(d.name, d.getvalue()) for d in docs]
                            api_client.upload_multiple_documents(payload)
                            doc_names = ", ".join([d.name for d in docs])
                            st.session_state["messages"].append({
                                "role": "user",
                                "content": f"📎 Attached {len(docs)} document(s): `{doc_names}`" + (f"\n\n**Note**: {instruction}" if instruction else ""),
                                "modality": "document"
                            })
                            query = instruction or f"Please summarize the main insights from: {doc_names}"
                            res = api_client.send_chat_message(
                                message=query,
                                conversation_id=conv_id,
                                enable_emotional_support=False,
                                enable_rag=True,
                                user_email=user_email
                            )
                            st.session_state["conversation_id"] = res["conversation_id"]
                            st.session_state["messages"].append({
                                "id": res["message_id"],
                                "role": "assistant",
                                "content": res["response"],
                                "modality": "text",
                                "metadata": {"citations": res.get("citations", [])}
                            })

                        # Process Images
                        for img in imgs:
                            img_prompt = instruction or "Please analyze and describe this visual in detail."
                            res = api_client.send_image_message(
                                file_bytes=img.getvalue(),
                                filename=img.name,
                                prompt=img_prompt,
                                conversation_id=conv_id
                            )
                            st.session_state["conversation_id"] = res["conversation_id"]
                            st.session_state["messages"].append({
                                "role": "user",
                                "content": f"🖼️ Analyzed image `{img.name}`: {img_prompt}",
                                "modality": "image"
                            })
                            st.session_state["messages"].append({
                                "id": res["message_id"],
                                "role": "assistant",
                                "content": res["response"],
                                "modality": "text"
                            })

                        # Process Audio
                        for aud in audios:
                            res = api_client.send_audio_message(
                                file_bytes=aud.getvalue(),
                                filename=aud.name,
                                conversation_id=conv_id
                            )
                            st.session_state["conversation_id"] = res["conversation_id"]
                            st.session_state["messages"].append({
                                "role": "user",
                                "content": f"🎙️ Audio memo `{aud.name}`: *\"{res.get('transcript', '')}\"*",
                                "modality": "audio"
                            })
                            st.session_state["messages"].append({
                                "id": res["message_id"],
                                "role": "assistant",
                                "content": res["response"],
                                "modality": "text"
                            })

                        st.session_state["show_attach_tray"] = False
                        st.toast("Files processed successfully!", icon="✅")
                        st.rerun()

            with col_close:
                if st.button("Close", key="btn_close_attach_tray", use_container_width=True):
                    st.session_state["show_attach_tray"] = False
                    st.rerun()

    # 2. Voice Drawer (Shown when '🎙️ Voice Note' is toggled)
    if st.session_state.get("show_voice_tray"):
        with st.container(border=True):
            st.markdown("#### 🎙️ Voice Input (Groq Whisper)")
            st.caption("Record your voice note or query below:")

            audio_data = st.audio_input("Record voice query:", key="jivan_voice_audio_in_tray")
            col_v1, col_v2 = st.columns([0.7, 0.3])
            with col_v1:
                if audio_data and st.button("🚀 Transcribe & Submit", type="primary", use_container_width=True, key="btn_submit_voice_tray"):
                    with st.spinner("Transcribing speech with Whisper..."):
                        conv_id = st.session_state.get("conversation_id")
                        user_email = st.session_state.get("user_email", "shubham@jivan.ai")
                        res = api_client.send_audio_message(
                            file_bytes=audio_data.getvalue(),
                            filename="recording.wav",
                            conversation_id=conv_id,
                            enable_tts=st.session_state.get("enable_tts", False)
                        )
                        st.session_state["conversation_id"] = res["conversation_id"]
                        st.session_state["messages"].append({
                            "role": "user",
                            "content": f"🎙️ Voice query: *\"{res.get('transcript', '')}\"*",
                            "modality": "audio"
                        })
                        st.session_state["messages"].append({
                            "id": res["message_id"],
                            "role": "assistant",
                            "content": res["response"],
                            "modality": "text",
                            "audio_base64": res.get("audio_base64")
                        })
                        st.session_state["show_voice_tray"] = False
                        st.rerun()
            with col_v2:
                if st.button("Close", key="btn_close_voice_tray", use_container_width=True):
                    st.session_state["show_voice_tray"] = False
                    st.rerun()
