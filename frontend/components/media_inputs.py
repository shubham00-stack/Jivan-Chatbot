import streamlit as st
from frontend.utils.api_client import api_client

def render_media_inputs():
    with st.expander("📎 Multimodal Attachments (Image & Audio)", expanded=False):
        tab_img, tab_audio = st.tabs(["🖼️ Image Analysis", "🎙️ Audio Recording"])

        # Tab 1: Image Analysis
        with tab_img:
            uploaded_img = st.file_uploader(
                "Upload Image (PNG, JPG, JPEG, WEBP)",
                type=["png", "jpg", "jpeg", "webp"],
                key="chat_image_uploader"
            )
            img_prompt = st.text_input(
                "What would you like to ask about this image?",
                value="Please describe and explain what you see in this image.",
                key="img_prompt_input"
            )
            if uploaded_img is not None:
                st.image(uploaded_img, caption="Image Preview", width=300)
                if st.button("🚀 Analyze Image", type="primary", key="btn_send_img"):
                    with st.spinner("Analyzing image content..."):
                        try:
                            conv_id = st.session_state.get("conversation_id")
                            res = api_client.send_image_message(
                                file_bytes=uploaded_img.getvalue(),
                                filename=uploaded_img.name,
                                prompt=img_prompt,
                                conversation_id=conv_id
                            )
                            # Update conversation ID
                            st.session_state["conversation_id"] = res["conversation_id"]

                            # Append messages to session state
                            st.session_state["messages"].append({
                                "role": "user",
                                "content": f"[Image: {uploaded_img.name}] {img_prompt}",
                                "modality": "image"
                            })
                            st.session_state["messages"].append({
                                "id": res["message_id"],
                                "role": "assistant",
                                "content": res["response"],
                                "modality": "text",
                                "metadata": {"model": res.get("model_used")}
                            })
                            st.rerun()
                        except Exception as e:
                            st.error(f"Image analysis error: {e}")

        # Tab 2: Audio Recording & Transcription
        with tab_audio:
            uploaded_audio = st.file_uploader(
                "Upload Voice Recording (WAV, MP3, M4A, OGG)",
                type=["wav", "mp3", "m4a", "ogg"],
                key="chat_audio_uploader"
            )
            if uploaded_audio is not None:
                st.audio(uploaded_audio)
                if st.button("🎙️ Process Voice Message", type="primary", key="btn_send_audio"):
                    with st.spinner("Transcribing audio and processing query..."):
                        try:
                            conv_id = st.session_state.get("conversation_id")
                            enable_tts = st.session_state.get("enable_tts", False)
                            res = api_client.send_audio_message(
                                file_bytes=uploaded_audio.getvalue(),
                                filename=uploaded_audio.name,
                                conversation_id=conv_id,
                                enable_tts=enable_tts
                            )
                            st.session_state["conversation_id"] = res["conversation_id"]

                            st.session_state["messages"].append({
                                "role": "user",
                                "content": f"🎙️ *\"{res['transcript']}\"*",
                                "modality": "audio"
                            })
                            st.session_state["messages"].append({
                                "id": res["message_id"],
                                "role": "assistant",
                                "content": res["response"],
                                "modality": "text",
                                "audio_base64": res.get("audio_base64"),
                                "metadata": {
                                    "citations": res.get("citations", []),
                                    "intent": res.get("intent")
                                }
                            })
                            st.rerun()
                        except Exception as e:
                            st.error(f"Audio processing error: {e}")

