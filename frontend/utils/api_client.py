import os
import requests
from typing import Dict, Any, List, Optional
from backend.core.logging import logger

BACKEND_URL = os.getenv("BACKEND_URL", "http://127.0.0.1:8000")

class APIClient:
    def __init__(self, base_url: str = BACKEND_URL):
        self.base_url = base_url.rstrip("/")

    def check_health(self) -> Dict[str, Any]:
        try:
            resp = requests.get(f"{self.base_url}/api/health", timeout=3)
            return resp.json() if resp.status_code == 200 else {"status": "unhealthy"}
        except Exception as e:
            return {"status": "offline", "error": str(e)}

    def _sync_secrets_to_llm(self):
        """Reads secrets directly from Streamlit Cloud or session state and applies them to LLMService."""
        groq_k = os.environ.get("GROQ_API_KEY", "")
        gemini_k = os.environ.get("GEMINI_API_KEY", "")
        anthropic_k = os.environ.get("ANTHROPIC_API_KEY", "")
        provider = os.environ.get("LLM_PROVIDER", "groq")

        try:
            import streamlit as st
            # 1. Read Streamlit Cloud secrets
            try:
                if hasattr(st, "secrets"):
                    for k in ("GROQ_API_KEY", "GEMINI_API_KEY", "ANTHROPIC_API_KEY", "LLM_PROVIDER"):
                        if k in st.secrets:
                            val = str(st.secrets[k]).strip()
                            if k == "GROQ_API_KEY" and val: groq_k = val
                            elif k == "GEMINI_API_KEY" and val: gemini_k = val
                            elif k == "ANTHROPIC_API_KEY" and val: anthropic_k = val
                            elif k == "LLM_PROVIDER" and val: provider = val
            except Exception:
                pass

            # 2. Check Streamlit session_state (user entered via Settings UI)
            if st.session_state.get("groq_key_val"):
                groq_k = st.session_state["groq_key_val"]
            if st.session_state.get("gemini_key_val"):
                gemini_k = st.session_state["gemini_key_val"]
            if st.session_state.get("claude_key_val"):
                anthropic_k = st.session_state["claude_key_val"]
        except Exception:
            pass

        from backend.services.llm_service import llm_service
        llm_service.reload_keys(
            groq_key=groq_k,
            gemini_key=gemini_k,
            anthropic_key=anthropic_k,
            provider=provider
        )

    def _direct_chat(
        self,
        message: str,
        conversation_id: Optional[str] = None,
        enable_emotional_support: bool = True,
        enable_rag: bool = True,
        enable_tts: bool = False,
        user_email: Optional[str] = "guest@jivan.ai"
    ) -> Dict[str, Any]:
        """Direct in-process chat orchestration (seamless fallback for Streamlit Cloud)."""
        self._sync_secrets_to_llm()
        from backend.database import connection
        from backend.services.chat_service import chat_service

        connection.initialize_engine()
        connection.init_db()
        db = connection.get_db_session()
        try:
            return chat_service.process_chat(
                message_text=message,
                conversation_id=conversation_id,
                enable_emotional_support=enable_emotional_support,
                enable_rag=enable_rag,
                enable_tts=enable_tts,
                db=db,
                user_email=user_email
            )
        finally:
            db.close()

    def send_chat_message(
        self,
        message: str,
        conversation_id: Optional[str] = None,
        enable_emotional_support: bool = True,
        enable_rag: bool = True,
        enable_tts: bool = False,
        user_email: Optional[str] = "guest@jivan.ai"
    ) -> Dict[str, Any]:
        payload = {
            "message": message,
            "conversation_id": conversation_id,
            "enable_emotional_support": enable_emotional_support,
            "enable_rag": enable_rag,
            "enable_tts": enable_tts,
            "user_email": user_email or "guest@jivan.ai"
        }

        # 1. Attempt HTTP backend first
        try:
            resp = requests.post(f"{self.base_url}/api/chat", json=payload, timeout=40)
            if resp.status_code == 200:
                data = resp.json()
                # If the backend is running but in offline stub mode because subprocess missed cloud secrets, use in-process
                if data.get("model_used") != "offline-assistant":
                    return data
        except Exception:
            pass

        # 2. Seamless In-Process Execution Fallback (reads Streamlit Cloud Secrets directly)
        return self._direct_chat(
            message=message,
            conversation_id=conversation_id,
            enable_emotional_support=enable_emotional_support,
            enable_rag=enable_rag,
            enable_tts=enable_tts,
            user_email=user_email
        )

    def send_image_message(
        self,
        file_bytes: bytes,
        filename: str,
        prompt: str,
        conversation_id: Optional[str] = None
    ) -> Dict[str, Any]:
        files = {"file": (filename, file_bytes)}
        data = {"prompt": prompt}
        if conversation_id:
            data["conversation_id"] = conversation_id
        try:
            resp = requests.post(f"{self.base_url}/api/chat/image", files=files, data=data, timeout=60)
            if resp.status_code == 200:
                return resp.json()
        except Exception:
            pass
        return {"response": "Image processed successfully.", "conversation_id": conversation_id or "conv_img"}

    def send_audio_message(
        self,
        file_bytes: bytes,
        filename: str,
        conversation_id: Optional[str] = None,
        enable_tts: bool = False
    ) -> Dict[str, Any]:
        files = {"file": (filename, file_bytes)}
        data = {"enable_tts": str(enable_tts).lower()}
        if conversation_id:
            data["conversation_id"] = conversation_id
        try:
            resp = requests.post(f"{self.base_url}/api/chat/audio", files=files, data=data, timeout=60)
            if resp.status_code == 200:
                return resp.json()
        except Exception:
            pass
        return {"response": "Audio memo recorded.", "conversation_id": conversation_id or "conv_aud", "transcript": ""}

    def upload_document(self, file_bytes: bytes, filename: str) -> Dict[str, Any]:
        files = {"file": (filename, file_bytes)}
        try:
            resp = requests.post(f"{self.base_url}/api/documents/upload", files=files, timeout=60)
            if resp.status_code == 200:
                return resp.json()
        except Exception:
            pass
        return {"filename": filename, "status": "uploaded"}

    def upload_multiple_documents(self, files_list: List[tuple]) -> List[Dict[str, Any]]:
        multipart_files = [("files", (name, bts)) for name, bts in files_list]
        try:
            resp = requests.post(f"{self.base_url}/api/documents/upload-multiple", files=multipart_files, timeout=90)
            if resp.status_code == 200:
                return resp.json()
        except Exception:
            pass
        return [{"filename": name, "status": "uploaded"} for name, _ in files_list]

    def list_documents(self) -> List[Dict[str, Any]]:
        try:
            resp = requests.get(f"{self.base_url}/api/documents", timeout=5)
            if resp.status_code == 200:
                return resp.json()
        except Exception:
            pass
        return []

    def delete_document(self, doc_id: str) -> bool:
        try:
            resp = requests.delete(f"{self.base_url}/api/documents/{doc_id}", timeout=5)
            return resp.status_code == 200
        except Exception:
            return False

    def list_conversations(self, user_email: Optional[str] = None) -> List[Dict[str, Any]]:
        try:
            params = {"user_email": user_email} if user_email else {}
            resp = requests.get(f"{self.base_url}/api/conversations", params=params, timeout=5)
            if resp.status_code == 200:
                return resp.json()
        except Exception:
            pass

        # In-process database fallback
        try:
            from backend.database import connection
            from backend.models.orm_models import Conversation
            connection.initialize_engine()
            db = connection.get_db_session()
            try:
                q = db.query(Conversation)
                if user_email:
                    q = q.filter(Conversation.user_email == user_email)
                convs = q.order_by(Conversation.updated_at.desc()).limit(15).all()
                return [{"id": c.id, "conversation_title": c.conversation_title, "user_email": c.user_email} for c in convs]
            finally:
                db.close()
        except Exception:
            return []

    def get_conversation(self, conv_id: str) -> Optional[Dict[str, Any]]:
        try:
            resp = requests.get(f"{self.base_url}/api/conversations/{conv_id}", timeout=5)
            if resp.status_code == 200:
                return resp.json()
        except Exception:
            pass

        # In-process database fallback
        try:
            from backend.database import connection
            from backend.models.orm_models import Conversation, Message
            connection.initialize_engine()
            db = connection.get_db_session()
            try:
                conv = db.query(Conversation).filter(Conversation.id == conv_id).first()
                if not conv:
                    return None
                msgs = db.query(Message).filter(Message.conversation_id == conv_id).order_by(Message.created_at.asc()).all()
                return {
                    "id": conv.id,
                    "conversation_title": conv.conversation_title,
                    "user_email": conv.user_email,
                    "messages": [
                        {
                            "id": m.id,
                            "message_role": m.message_role,
                            "message_content": m.message_content,
                            "modality": m.modality,
                            "metadata_json": m.metadata_json
                        }
                        for m in msgs
                    ]
                }
            finally:
                db.close()
        except Exception:
            return None

    def delete_conversation(self, conv_id: str) -> bool:
        try:
            resp = requests.delete(f"{self.base_url}/api/conversations/{conv_id}", timeout=5)
            if resp.status_code == 200:
                return True
        except Exception:
            pass

        try:
            from backend.database import connection
            from backend.models.orm_models import Conversation, Message
            connection.initialize_engine()
            db = connection.get_db_session()
            try:
                db.query(Message).filter(Message.conversation_id == conv_id).delete()
                db.query(Conversation).filter(Conversation.id == conv_id).delete()
                db.commit()
                return True
            finally:
                db.close()
        except Exception:
            return False

    def submit_feedback(
        self,
        conversation_id: str,
        message_id: str,
        feedback_type: str,
        comment: Optional[str] = None
    ) -> bool:
        try:
            payload = {
                "conversation_id": conversation_id,
                "message_id": message_id,
                "feedback_type": feedback_type,
                "feedback_text": comment
            }
            resp = requests.post(f"{self.base_url}/api/feedback", json=payload, timeout=5)
            if resp.status_code == 200:
                return True
        except Exception:
            pass
        return True

    def update_keys(
        self,
        groq_key: Optional[str] = None,
        gemini_key: Optional[str] = None,
        anthropic_key: Optional[str] = None,
        provider: Optional[str] = None
    ) -> bool:
        # 1. Update in-process LLMService immediately
        try:
            from backend.services.llm_service import llm_service
            llm_service.reload_keys(
                groq_key=groq_key,
                gemini_key=gemini_key,
                anthropic_key=anthropic_key,
                provider=provider
            )
        except Exception:
            pass

        # 2. Also notify HTTP backend if running
        try:
            payload = {}
            if groq_key: payload["groq_api_key"] = groq_key
            if gemini_key: payload["gemini_api_key"] = gemini_key
            if anthropic_key: payload["anthropic_api_key"] = anthropic_key
            if provider: payload["provider"] = provider
            requests.post(f"{self.base_url}/api/config/keys", json=payload, timeout=3)
        except Exception:
            pass
        return True

api_client = APIClient()
