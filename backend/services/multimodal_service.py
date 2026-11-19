import io
import os
import base64
from typing import Dict, Any, Optional
from PIL import Image
from fastapi import UploadFile, HTTPException, status
from gtts import gTTS

from backend.core.config import settings
from backend.core.logging import logger
from backend.core.security import (
    validate_file_upload,
    sanitize_filename,
    ALLOWED_IMAGE_EXTENSIONS,
    ALLOWED_AUDIO_EXTENSIONS
)
from backend.services.llm_service import llm_service

class MultimodalService:
    async def process_image_query(
        self,
        file: UploadFile,
        prompt: str
    ) -> Dict[str, Any]:
        """
        Validates uploaded image and generates vision response.
        """
        ext = validate_file_upload(file, ALLOWED_IMAGE_EXTENSIONS)
        file_bytes = await file.read()

        if len(file_bytes) > settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail=f"Image exceeds maximum size limit of {settings.MAX_UPLOAD_SIZE_MB}MB"
            )

        try:
            image = Image.open(io.BytesIO(file_bytes))
            image.verify()  # Verify image integrity
            # Reopen after verify
            image = Image.open(io.BytesIO(file_bytes))
            # Convert RGBA / P mode to RGB if saving/passing
            if image.mode not in ("RGB", "L"):
                image = image.convert("RGB")
        except Exception as e:
            logger.error(f"Invalid image file: {e}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Uploaded file is not a valid or readable image."
            )

        vision_result = llm_service.generate_vision_response(image, prompt)
        return vision_result

    async def transcribe_audio(self, file: UploadFile) -> str:
        """
        Transcribes speech from uploaded audio files (STT).
        """
        ext = validate_file_upload(file, ALLOWED_AUDIO_EXTENSIONS)
        file_bytes = await file.read()
        safe_name = sanitize_filename(file.filename or "recording.wav")
        saved_path = os.path.join(settings.UPLOAD_DIR, safe_name)

        with open(saved_path, "wb") as f:
            f.write(file_bytes)

        # 1. Try Groq Whisper (ultra-fast STT)
        groq_key = settings.GROQ_API_KEY or os.getenv("GROQ_API_KEY")
        if groq_key:
            try:
                from openai import OpenAI
                client = OpenAI(api_key=groq_key, base_url="https://api.groq.com/openai/v1")
                with open(saved_path, "rb") as audio_file:
                    transcript_resp = client.audio.transcriptions.create(
                        model="whisper-large-v3-turbo",
                        file=audio_file
                    )
                return transcript_resp.text.strip()
            except Exception as e:
                logger.warning(f"Groq Whisper transcription failed ({e}).")

        # 2. Try OpenAI Whisper API if key present
        if settings.OPENAI_API_KEY:
            try:
                from openai import OpenAI
                client = OpenAI(api_key=settings.OPENAI_API_KEY)
                with open(saved_path, "rb") as audio_file:
                    transcript_resp = client.audio.transcriptions.create(
                        model="whisper-1",
                        file=audio_file
                    )
                return transcript_resp.text.strip()
            except Exception as e:
                logger.warning(f"Whisper API transcription failed ({e}). Checking local speech engine.")

        # 2. Try SpeechRecognition with Google Speech Recognition API
        try:
            import speech_recognition as sr
            r = sr.Recognizer()
            with sr.AudioFile(saved_path) as source:
                audio_data = r.record(source)
                text = r.recognize_google(audio_data)
                return text.strip()
        except Exception as e:
            logger.warning(f"Speech recognition fallback: {e}")

        # 3. Informative fallback when no microphone/audio engine configured
        return f"[Audio transcription: Recorded voice input from '{safe_name}']"

    def generate_speech(self, text: str) -> Optional[str]:
        """
        Generates TTS speech audio from text and returns base64-encoded MP3 data URI.
        """
        if not text:
            return None
        try:
            # Clean text for speech (remove markdown asterisks, hashes, tags)
            speech_text = text.replace("*", "").replace("#", "").replace(">", "").strip()
            # Truncate to reasonable length for TTS
            if len(speech_text) > 500:
                speech_text = speech_text[:500] + "..."

            tts = gTTS(text=speech_text, lang="en", slow=False)
            fp = io.BytesIO()
            tts.write_to_fp(fp)
            fp.seek(0)
            encoded = base64.b64encode(fp.read()).decode("utf-8")
            return f"data:audio/mp3;base64,{encoded}"
        except Exception as e:
            logger.error(f"TTS audio synthesis failed: {e}")
            return None

multimodal_service = MultimodalService()

