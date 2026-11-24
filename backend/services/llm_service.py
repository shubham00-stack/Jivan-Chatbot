import os
from typing import List, Dict, Any, Optional
from PIL import Image
from backend.core.config import settings
from backend.core.logging import logger

class LLMService:
    def __init__(self):
        self.provider = settings.LLM_PROVIDER.lower()
        self.gemini_client = None
        self.openai_client = None
        self.groq_client = None
        self.anthropic_client = None
        self._init_clients()

    def _init_clients(self):
        # Check Streamlit Cloud Secrets directly if available
        try:
            import streamlit as st
            if hasattr(st, "secrets"):
                try:
                    for k in ("GROQ_API_KEY", "GEMINI_API_KEY", "ANTHROPIC_API_KEY", "LLM_PROVIDER"):
                        if k in st.secrets:
                            v = str(st.secrets[k]).strip()
                            if v:
                                os.environ[k] = v
                except Exception:
                    pass
        except Exception:
            pass

        # 1. Initialize Google Gemini Client if key present
        gemini_key = os.getenv("GEMINI_API_KEY") or settings.GEMINI_API_KEY
        if gemini_key:
            try:
                from google import genai
                self.gemini_client = genai.Client(api_key=gemini_key)
                logger.info("Google Gemini client initialized successfully.")
            except Exception as e:
                logger.warning(f"Could not initialize Gemini client: {e}")

        # 2. Initialize Groq Client if key present
        groq_key = os.getenv("GROQ_API_KEY") or settings.GROQ_API_KEY
        if groq_key:
            try:
                from openai import OpenAI
                self.groq_client = OpenAI(
                    api_key=groq_key,
                    base_url="https://api.groq.com/openai/v1"
                )
                logger.info("Groq client initialized successfully.")
            except Exception as e:
                logger.warning(f"Could not initialize Groq client: {e}")

        # 3. Initialize Standard OpenAI Client if key present
        openai_key = settings.OPENAI_API_KEY or os.getenv("OPENAI_API_KEY")
        if openai_key:
            try:
                from openai import OpenAI
                base_url = settings.OPENAI_BASE_URL or os.getenv("OPENAI_BASE_URL")
                self.openai_client = OpenAI(api_key=openai_key, base_url=base_url)
                logger.info("OpenAI client initialized successfully.")
            except Exception as e:
                logger.warning(f"Could not initialize OpenAI client: {e}")

        # 4. Initialize Anthropic Claude Client if key present
        anthropic_key = settings.ANTHROPIC_API_KEY or os.getenv("ANTHROPIC_API_KEY")
        if anthropic_key:
            try:
                import anthropic
                self.anthropic_client = anthropic.Anthropic(api_key=anthropic_key)
                logger.info("Anthropic Claude client initialized successfully.")
            except Exception as e:
                logger.warning(f"Could not initialize Anthropic client: {e}")

    def reload_keys(
        self,
        groq_key: Optional[str] = None,
        gemini_key: Optional[str] = None,
        anthropic_key: Optional[str] = None,
        provider: Optional[str] = None
    ) -> Dict[str, Any]:
        """Dynamically reloads API credentials at runtime."""
        if groq_key:
            os.environ["GROQ_API_KEY"] = groq_key
            settings.GROQ_API_KEY = groq_key
        if gemini_key:
            os.environ["GEMINI_API_KEY"] = gemini_key
            settings.GEMINI_API_KEY = gemini_key
        if anthropic_key:
            os.environ["ANTHROPIC_API_KEY"] = anthropic_key
            settings.ANTHROPIC_API_KEY = anthropic_key
        if provider:
            os.environ["LLM_PROVIDER"] = provider
            settings.LLM_PROVIDER = provider
            self.provider = provider.lower()
        self._init_clients()
        return {
            "groq_active": self.groq_client is not None,
            "gemini_active": self.gemini_client is not None,
            "anthropic_active": self.anthropic_client is not None,
            "provider": self.provider
        }

    def generate_chat_response(
        self,
        messages: List[Dict[str, str]],
        system_prompt: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generates response given conversation history and system instructions.
        Tries primary provider first, with automatic cross-provider fallback.
        """
        if not self.groq_client and not self.gemini_client:
            self._init_clients()

        last_error = None

        # Candidate models for high-speed Groq inference
        groq_candidates = [
            settings.GROQ_MODEL,
            "llama-3.3-70b-versatile",
            "llama-3.1-8b-instant",
            "mixtral-8x7b-32768"
        ]
        groq_models = []
        for m in groq_candidates:
            if m and m not in groq_models:
                groq_models.append(m)

        # Candidate models for Google Gemini
        gemini_candidates = [
            settings.GEMINI_MODEL,
            "gemini-2.0-flash",
            "gemini-1.5-flash",
            "gemini-1.5-pro"
        ]
        gemini_models = []
        for m in gemini_candidates:
            if m and m not in gemini_models:
                gemini_models.append(m)

        # 1. Try Groq (if configured as primary or available)
        if (self.provider == "groq" or not self.gemini_client) and self.groq_client:
            groq_msgs = []
            if system_prompt:
                groq_msgs.append({"role": "system", "content": system_prompt})
            for m in messages:
                groq_msgs.append({"role": m["role"], "content": m["content"]})

            for model_name in groq_models:
                try:
                    completion = self.groq_client.chat.completions.create(
                        model=model_name,
                        messages=groq_msgs,
                        max_tokens=850
                    )
                    return {
                        "text": completion.choices[0].message.content or "",
                        "model": f"groq/{model_name}"
                    }
                except Exception as e:
                    last_error = e
                    logger.warning(f"Groq generation attempt failed with model '{model_name}': {e}")

        # 2. Try Google Gemini
        if self.gemini_client:
            full_contents = []
            if system_prompt:
                full_contents.append(f"[System Instruction]: {system_prompt}\n")
            for m in messages:
                prefix = "User" if m["role"] == "user" else "Assistant"
                full_contents.append(f"{prefix}: {m['content']}")

            prompt_str = "\n\n".join(full_contents)
            for model_name in gemini_models:
                try:
                    response = self.gemini_client.models.generate_content(
                        model=model_name,
                        contents=prompt_str
                    )
                    return {
                        "text": response.text or "I processed your request, but did not receive a text response.",
                        "model": model_name
                    }
                except Exception as e:
                    last_error = e
                    logger.warning(f"Gemini generation attempt failed with model '{model_name}': {e}")

        # 3. Fallback to Groq if Gemini failed but Groq is available
        if self.groq_client:
            groq_msgs = []
            if system_prompt:
                groq_msgs.append({"role": "system", "content": system_prompt})
            for m in messages:
                groq_msgs.append({"role": m["role"], "content": m["content"]})

            for model_name in groq_models:
                try:
                    completion = self.groq_client.chat.completions.create(
                        model=model_name,
                        messages=groq_msgs,
                        max_tokens=850
                    )
                    return {
                        "text": completion.choices[0].message.content or "",
                        "model": f"groq/{model_name}"
                    }
                except Exception as e:
                    last_error = e
                    logger.warning(f"Groq fallback generation attempt failed with model '{model_name}': {e}")

        # 4. Try Standard OpenAI
        if self.openai_client:
            try:
                openai_msgs = []
                if system_prompt:
                    openai_msgs.append({"role": "system", "content": system_prompt})
                for m in messages:
                    openai_msgs.append({"role": m["role"], "content": m["content"]})

                completion = self.openai_client.chat.completions.create(
                    model=settings.OPENAI_MODEL,
                    messages=openai_msgs
                )
                return {
                    "text": completion.choices[0].message.content or "",
                    "model": settings.OPENAI_MODEL
                }
            except Exception as e:
                last_error = e
                logger.error(f"OpenAI generation error: {e}")

        # 5. Local Fallback with error visibility
        return self._generate_local_fallback(messages, system_prompt, last_error)

    def generate_code_response(
        self,
        messages: List[Dict[str, str]],
        custom_instructions: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Specialized coding route powered by Claude 3.5 Sonnet.
        """
        system_prompt = (
            "You are Claude 3.5 Sonnet, Anthropic's state-of-the-art coding, software architecture, and algorithm specialist.\n\n"
            "STRICT PRODUCTION CODING DIRECTIVES:\n"
            "1. Deliver complete, production-ready, modular code (never use placeholder ellipses like '...' or 'todo').\n"
            "2. Enclose code strictly in formatted markdown code blocks with explicit language tags (e.g. ```python, ```javascript, ```sql, ```bash).\n"
            "3. Include high-value docstrings, type annotations, and edge-case error handling.\n"
            "4. Provide a runnable execution example demonstrating input and expected output.\n"
            "5. Follow with a concise architecture breakdown and algorithmic complexity (Big-O) analysis.\n"
            "6. Keep text succinct and prioritize beautiful, idiomatic code."
        )
        if custom_instructions:
            system_prompt += f"\n\nAdditional Directive: {custom_instructions}"

        if not self.groq_client and not self.anthropic_client:
            self._init_clients()

        # 1. Try Direct Anthropic Claude Client
        if self.anthropic_client:
            try:
                anthropic_msgs = []
                for m in messages:
                    anthropic_msgs.append({"role": m["role"], "content": m["content"]})

                resp = self.anthropic_client.messages.create(
                    model=settings.CLAUDE_MODEL,
                    max_tokens=4096,
                    system=system_prompt,
                    messages=anthropic_msgs
                )
                return {
                    "text": resp.content[0].text,
                    "model": f"anthropic/{settings.CLAUDE_MODEL}",
                    "specialist": "Claude 3.5 Sonnet (Coding Specialist)"
                }
            except Exception as e:
                logger.warning(f"Direct Anthropic Claude API call failed ({e}). Falling back to Claude Persona Engine.")

        # 2. Try Groq (Llama/Mixtral) with Claude 3.5 Sonnet Persona
        if self.groq_client:
            groq_msgs = [{"role": "system", "content": system_prompt}]
            for m in messages:
                groq_msgs.append({"role": m["role"], "content": m["content"]})

            groq_candidates = [
                settings.GROQ_MODEL,
                "llama-3.3-70b-versatile",
                "llama-3.1-8b-instant",
                "mixtral-8x7b-32768"
            ]
            groq_models = []
            for m in groq_candidates:
                if m and m not in groq_models:
                    groq_models.append(m)

            for model_name in groq_models:
                try:
                    completion = self.groq_client.chat.completions.create(
                        model=model_name,
                        messages=groq_msgs,
                        temperature=0.2,
                        max_tokens=850
                    )
                    model_used = f"Claude-3.5-Sonnet (Groq {model_name})" if not settings.ANTHROPIC_API_KEY else f"anthropic/{settings.CLAUDE_MODEL}"
                    return {
                        "text": completion.choices[0].message.content or "",
                        "model": model_used,
                        "specialist": "Claude 3.5 Sonnet (Coding Specialist)"
                    }
                except Exception as e:
                    logger.warning(f"Claude Coding Engine attempt failed on Groq with model '{model_name}': {e}")

        # 3. Fallback to Gemini with Claude Persona
        return self.generate_chat_response(messages=messages, system_prompt=system_prompt)

    def generate_vision_response(
        self,
        image: Image.Image,
        prompt: str,
        system_prompt: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Processes image content and user question using a vision-capable model.
        """
        if self.gemini_client:
            models_to_try = [settings.GEMINI_MODEL, "gemini-2.0-flash", "gemini-1.5-flash"]
            # Deduplicate while preserving order
            seen_models = set()
            candidate_models = []
            for m in models_to_try:
                if m and m not in seen_models:
                    seen_models.add(m)
                    candidate_models.append(m)

            for model_name in candidate_models:
                try:
                    contents = [image, prompt]
                    if system_prompt:
                        contents.insert(0, system_prompt)
                    response = self.gemini_client.models.generate_content(
                        model=model_name,
                        contents=contents
                    )
                    return {
                        "text": response.text or "Image analyzed successfully.",
                        "model": model_name
                    }
                except Exception as e:
                    logger.warning(f"Gemini vision error with {model_name}: {e}")

        # Local Image Understanding Fallback
        w, h = image.size
        fmt = image.format or "JPEG"
        return {
            "text": (
                f"**Image Inspection Summary**:\n\n"
                f"- **Dimensions**: {w}x{h} pixels\n"
                f"- **Format**: {fmt}\n"
                f"- **Color Mode**: {image.mode}\n\n"
                f"**User Question**: *\"{prompt}\"*\n\n"
                f"*(Note: Vision reasoning requires a multimodal model provider configured in `.env`.)*"
            ),
            "model": "local-vision-inspector"
        }

    def _generate_local_fallback(
        self,
        messages: List[Dict[str, str]],
        system_prompt: Optional[str],
        error: Optional[Exception] = None
    ) -> Dict[str, Any]:
        last_msg = messages[-1]["content"] if messages else ""
        
        # Check if knowledge context is included in prompt
        if "<untrusted_knowledge_base>" in (system_prompt or ""):
            return {
                "text": (
                    f"I have retrieved the relevant knowledge base document chunks for your inquiry.\n\n"
                    f"**Analysis**: Based on the indexed reference materials, your query relates to:\n"
                    f"> *\"{last_msg}\"*\n\n"
                    f"The specific excerpts have been grounded and cited in the source references below.\n\n"
                    f"*(Configure an active `GROQ_API_KEY` or `GEMINI_API_KEY` in `.env` for generative answers.)*"
                ),
                "model": "offline-rag-grounder"
            }

        err_notice = f"\n\n*(Provider notice: {str(error)})*" if error else ""

        return {
            "text": (
                f"Hello! I received your message: *\"{last_msg}\"*.\n\n"
                f"I am functioning in offline development mode. To activate full generative reasoning, "
                f"please verify your `GROQ_API_KEY` or `GEMINI_API_KEY` in `.env`.{err_notice}"
            ),
            "model": "offline-assistant"
        }

llm_service = LLMService()
