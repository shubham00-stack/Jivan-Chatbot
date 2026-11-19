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
        try:
            resp = requests.post(f"{self.base_url}/api/chat", json=payload, timeout=60)
            resp.raise_for_status()
            return resp.json()
        except Exception as e:
            logger.error(f"Error in send_chat_message: {e}")
            raise e

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
            resp.raise_for_status()
            return resp.json()
        except Exception as e:
            logger.error(f"Error in send_image_message: {e}")
            raise e

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
            resp.raise_for_status()
            return resp.json()
        except Exception as e:
            logger.error(f"Error in send_audio_message: {e}")
            raise e

    def upload_document(self, file_bytes: bytes, filename: str) -> Dict[str, Any]:
        files = {"file": (filename, file_bytes)}
        try:
            resp = requests.post(f"{self.base_url}/api/documents/upload", files=files, timeout=60)
            resp.raise_for_status()
            return resp.json()
        except Exception as e:
            logger.error(f"Error in upload_document: {e}")
            raise e

    def upload_multiple_documents(self, files_list: List[tuple]) -> List[Dict[str, Any]]:
        multipart_files = [("files", (name, bts)) for name, bts in files_list]
        try:
            resp = requests.post(f"{self.base_url}/api/documents/upload-multiple", files=multipart_files, timeout=90)
            resp.raise_for_status()
            return resp.json()
        except Exception as e:
            logger.error(f"Error in upload_multiple_documents: {e}")
            raise e

    def list_documents(self) -> List[Dict[str, Any]]:
        try:
            resp = requests.get(f"{self.base_url}/api/documents", timeout=5)
            return resp.json() if resp.status_code == 200 else []
        except Exception as e:
            logger.warning(f"Could not list documents (backend offline/initializing): {e}")
            return []

    def delete_document(self, doc_id: str) -> bool:
        try:
            resp = requests.delete(f"{self.base_url}/api/documents/{doc_id}", timeout=5)
            return resp.status_code == 200
        except Exception as e:
            logger.warning(f"Could not delete document: {e}")
            return False

    def list_conversations(self, user_email: Optional[str] = None) -> List[Dict[str, Any]]:
        try:
            params = {"user_email": user_email} if user_email else {}
            resp = requests.get(f"{self.base_url}/api/conversations", params=params, timeout=5)
            return resp.json() if resp.status_code == 200 else []
        except Exception as e:
            logger.warning(f"Could not list conversations (backend offline/initializing): {e}")
            return []

    def get_conversation(self, conv_id: str) -> Optional[Dict[str, Any]]:
        try:
            resp = requests.get(f"{self.base_url}/api/conversations/{conv_id}", timeout=5)
            return resp.json() if resp.status_code == 200 else None
        except Exception as e:
            logger.warning(f"Could not get conversation: {e}")
            return None

    def delete_conversation(self, conv_id: str) -> bool:
        try:
            resp = requests.delete(f"{self.base_url}/api/conversations/{conv_id}", timeout=5)
            return resp.status_code == 200
        except Exception as e:
            logger.warning(f"Could not delete conversation: {e}")
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
            return resp.status_code == 200
        except Exception as e:
            logger.warning(f"Could not submit feedback: {e}")
            return False

api_client = APIClient()
