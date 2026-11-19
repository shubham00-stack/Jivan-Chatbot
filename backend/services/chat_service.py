import json
import re
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session

from backend.models.orm_models import Conversation, Message
from backend.services.safety_service import safety_service
from backend.services.emotional_support_service import emotional_support_service
from backend.services.rag_service import rag_service
from backend.services.llm_service import llm_service
from backend.services.multimodal_service import multimodal_service
from backend.services.generator_service import generator_service
from rag.vector_store import vector_store_manager
from backend.core.config import settings
from backend.core.logging import logger

def is_coding_request(text: str) -> bool:
    clean = text.lower().strip()
    if clean.startswith("/code") or clean.startswith("/python"):
        return True
    coding_patterns = [
        r"\bpython\b", r"\bjavascript\b", r"\btypescript\b", r"\bc\+\+\b", r"\bjava\b", r"\bsql\b",
        r"\bhtml\b", r"\bcss\b", r"\brust\b", r"\bgolang\b", r"\bcode\b", r"\bloop\b", r"\bfunction\b",
        r"\bclass\b", r"\bscript\b", r"\balgorithm\b", r"\bdebug\b", r"\bregex\b", r"\bapi endpoint\b",
        r"\bfastapi\b", r"\breact\b", r"\bstreamlit\b", r"\bprogram\b", r"\bcoding\b", r"\bfor loop\b",
        r"\bwhile loop\b", r"\bclaud ai\b", r"\bclaude\b"
    ]
    return any(re.search(p, clean) for p in coding_patterns)

class ChatService:
    def process_chat(
        self,
        message_text: str,
        conversation_id: Optional[str],
        enable_emotional_support: bool,
        enable_rag: bool,
        enable_tts: bool,
        db: Session,
        user_email: Optional[str] = "guest@jivan.ai"
    ) -> Dict[str, Any]:
        """
        End-to-end chat orchestration with specialized Multi-Model Routing:
        - Claude 3.5 Sonnet: Code & Software Engineering
        - Canva AI: Presentations & Slide Decks (.pptx)
        - Nano Banana AI 2.1: Image & Visual Art Generation
        - PyMuPDF & Chroma: Document Analysis & PDF Export
        - Sentinel & Wellness Engine: Safety & Emotional Support
        """
        # 1. Safety Sentinel Evaluation
        is_safe, is_crisis, safety_reply = safety_service.check_safety(message_text)

        # 2. Retrieve or create conversation record
        conv = None
        if conversation_id:
            conv = db.query(Conversation).filter(Conversation.id == conversation_id).first()

        if not conv:
            title = (message_text[:40] + "...") if len(message_text) > 40 else message_text
            conv = Conversation(conversation_title=title or "New Conversation", user_email=user_email or "guest@jivan.ai")
            db.add(conv)
            db.commit()
            db.refresh(conv)

        # 3. Persist User Message
        user_msg = Message(
            conversation_id=conv.id,
            message_role="user",
            message_content=message_text,
            modality="text"
        )
        db.add(user_msg)
        db.commit()

        # 4. Handle Immediate Safety Interception
        if not is_safe:
            intent = "crisis_intervention" if is_crisis else "security_block"
            response_text = safety_reply or "Request blocked by safety guardrails."
            
            asst_msg = Message(
                conversation_id=conv.id,
                message_role="assistant",
                message_content=response_text,
                modality="text",
                metadata_json=json.dumps({"intent": intent, "safety_triggered": True})
            )
            db.add(asst_msg)
            db.commit()
            db.refresh(asst_msg)

            audio_data = multimodal_service.generate_speech(response_text) if enable_tts else None

            return {
                "conversation_id": conv.id,
                "message_id": asst_msg.id,
                "response": response_text,
                "intent": intent,
                "citations": [],
                "audio_base64": audio_data,
                "emotional_support": is_crisis,
                "model_used": "safety-sentinel"
            }

        # 5. Load Conversation Context (last 10 messages)
        history_records = (
            db.query(Message)
            .filter(Message.conversation_id == conv.id)
            .order_by(Message.created_at.asc())
            .all()
        )
        formatted_messages = [
            {"role": m.message_role, "content": m.message_content}
            for m in history_records[-10:]
        ]

        # 4b. Slash Commands Processor
        stripped_msg = message_text.strip()
        if stripped_msg.startswith("/"):
            cmd_parts = stripped_msg.split(" ", 1)
            command = cmd_parts[0].lower()
            cmd_args = cmd_parts[1].strip() if len(cmd_parts) > 1 else ""

            if command == "/help":
                help_text = (
                    "### 🛠️ Specialized AI Command Reference\n\n"
                    "Each task is routed to its dedicated specialist model:\n\n"
                    "- **/code <request>**: Code with **Claude 3.5 Sonnet** (e.g. `/code write quicksort in python`)\n"
                    "- **/presentation <topic>**: Create a slide deck with **Canva AI** (e.g. `/presentation AI Market Trends`)\n"
                    "- **/image <prompt>**: Generate visual art with **Nano Banana AI 2.1** (e.g. `/image cute baby monkey`)\n"
                    "- **/pdf <topic>**: Export formatted PDF document (e.g. `/pdf Quantum Computing Overview`)\n"
                    "- **/search <query>**: Query the RAG document knowledge base\n"
                    "- **/coping**: Guided emotional wellness (5-4-3-2-1 exercise)\n"
                    "- **/model**: View active multi-model AI roster and database status"
                )
                asst_msg = Message(
                    conversation_id=conv.id,
                    message_role="assistant",
                    message_content=help_text,
                    modality="text",
                    metadata_json=json.dumps({"intent": "command_help"})
                )
                db.add(asst_msg)
                db.commit()
                db.refresh(asst_msg)
                return {
                    "conversation_id": conv.id,
                    "message_id": asst_msg.id,
                    "response": help_text,
                    "intent": "command_help",
                    "citations": [],
                    "audio_base64": None,
                    "emotional_support": False,
                    "model_used": "system-commands"
                }

            elif command in ("/code", "/python"):
                code_prompt = cmd_args or "Write a clean, optimized Python implementation."
                code_msgs = formatted_messages[:-1] + [{"role": "user", "content": code_prompt}]
                code_res = llm_service.generate_code_response(code_msgs)
                response_text = code_res["text"]
                specialist = code_res.get("specialist", "Claude 3.5 Sonnet (Coding Specialist)")

                asst_msg = Message(
                    conversation_id=conv.id,
                    message_role="assistant",
                    message_content=response_text,
                    modality="text",
                    metadata_json=json.dumps({"intent": "code_generation", "specialist": specialist, "model": code_res["model"]})
                )
                db.add(asst_msg)
                db.commit()
                db.refresh(asst_msg)
                return {
                    "conversation_id": conv.id,
                    "message_id": asst_msg.id,
                    "response": response_text,
                    "intent": "code_generation",
                    "citations": [],
                    "audio_base64": None,
                    "emotional_support": False,
                    "model_used": code_res["model"],
                    "specialist": specialist
                }

            elif command in ("/presentation", "/slides", "/canva", "/deck"):
                topic_arg = cmd_args or "Next-Generation Enterprise Artificial Intelligence"
                slide_prompt = (
                    f"Create a structured, 5-slide executive presentation outline about '{topic_arg}'.\n"
                    "Format strictly as:\n"
                    "# Slide 1: Title\n[Subtitle]\n\n"
                    "# Slide 2: Problem & Market Need\n- point 1\n- point 2\n- point 3\n\n"
                    "# Slide 3: Core Solution & Value Proposition\n- point 1\n- point 2\n- point 3\n\n"
                    "# Slide 4: Key Metrics & Impact\n- point 1\n- point 2\n- point 3\n\n"
                    "# Slide 5: Strategic Roadmap & Next Steps\n- point 1\n- point 2\n- point 3"
                )
                llm_res = llm_service.generate_chat_response(
                    messages=[{"role": "user", "content": slide_prompt}],
                    system_prompt="You are a premier executive presentation designer specializing in Canva slide decks."
                )
                gen_res = generator_service.generate_canva_presentation(topic_arg, llm_res["text"])
                response_text = gen_res["message"]
                db_gen_meta = {k: v for k, v in gen_res.items() if k not in ("data_uri", "file_bytes_b64")}
                asst_msg = Message(
                    conversation_id=conv.id,
                    message_role="assistant",
                    message_content=response_text,
                    modality="presentation",
                    metadata_json=json.dumps({"intent": "presentation_generation", "generated_file": db_gen_meta, "model": "Canva AI Engine"})
                )
                db.add(asst_msg)
                db.commit()
                db.refresh(asst_msg)
                return {
                    "conversation_id": conv.id,
                    "message_id": asst_msg.id,
                    "response": response_text,
                    "intent": "presentation_generation",
                    "citations": [],
                    "audio_base64": None,
                    "emotional_support": False,
                    "model_used": "Canva AI Engine",
                    "specialist": "Canva AI (Presentation Specialist)",
                    "generated_file": gen_res
                }

            elif command in ("/image", "/img"):
                prompt_arg = cmd_args or "a serene mountain sunrise landscape"
                gen_res = generator_service.generate_image(prompt_arg)
                response_text = gen_res["message"]
                db_gen_meta = {k: v for k, v in gen_res.items() if k not in ("data_uri", "file_bytes_b64")}
                asst_msg = Message(
                    conversation_id=conv.id,
                    message_role="assistant",
                    message_content=response_text,
                    modality="image",
                    metadata_json=json.dumps({"intent": "image_generation", "generated_file": db_gen_meta})
                )
                db.add(asst_msg)
                db.commit()
                db.refresh(asst_msg)
                return {
                    "conversation_id": conv.id,
                    "message_id": asst_msg.id,
                    "response": response_text,
                    "intent": "image_generation",
                    "citations": [],
                    "audio_base64": None,
                    "emotional_support": False,
                    "model_used": "Nano Banana AI 2.1",
                    "specialist": "Nano Banana AI (Visual Studio)",
                    "generated_file": gen_res
                }

            elif command == "/pdf":
                topic_arg = cmd_args or "Artificial Intelligence Overview"
                doc_chunks = rag_service.retrieve_relevant_chunks(topic_arg, top_k=4)
                sys_prompt = "You are a professional technical writer and document creator."
                if doc_chunks:
                    rag_ctx, _ = rag_service.build_grounded_system_prompt(doc_chunks)
                    sys_prompt = f"{rag_ctx}\n\nYou are writing an executive document based on the knowledge provided."

                doc_prompt = (
                    f"Write a structured, comprehensive document about '{topic_arg}' "
                    "with clear section headings (# Heading), key facts, bullet points (- point), detailed explanations, and a strategic conclusion. "
                    "Do not use conversational filler."
                )
                llm_res = llm_service.generate_chat_response(
                    messages=[{"role": "user", "content": doc_prompt}],
                    system_prompt=sys_prompt
                )
                doc_content = llm_res["text"]
                gen_res = generator_service.generate_pdf_document(topic_arg, doc_content)
                response_text = gen_res["message"]
                db_gen_meta = {k: v for k, v in gen_res.items() if k not in ("data_uri", "file_bytes_b64")}
                asst_msg = Message(
                    conversation_id=conv.id,
                    message_role="assistant",
                    message_content=response_text,
                    modality="document",
                    metadata_json=json.dumps({"intent": "document_generation", "generated_file": db_gen_meta, "model": llm_res["model"]})
                )
                db.add(asst_msg)
                db.commit()
                db.refresh(asst_msg)
                return {
                    "conversation_id": conv.id,
                    "message_id": asst_msg.id,
                    "response": response_text,
                    "intent": "document_generation",
                    "citations": [],
                    "audio_base64": None,
                    "emotional_support": False,
                    "model_used": llm_res["model"],
                    "specialist": "JIVAN PDF Document Studio",
                    "generated_file": gen_res
                }

            elif command in ("/search", "/rag"):
                query_arg = cmd_args or "general overview"
                chunks = rag_service.retrieve_relevant_chunks(query_arg, top_k=4, threshold=0.15)
                rag_prompt, citations = rag_service.build_grounded_system_prompt(chunks)
                llm_res = llm_service.generate_chat_response(
                    messages=[{"role": "user", "content": query_arg}],
                    system_prompt=rag_prompt
                )
                response_text = llm_res["text"]
                asst_msg = Message(
                    conversation_id=conv.id,
                    message_role="assistant",
                    message_content=response_text,
                    modality="text",
                    metadata_json=json.dumps({"intent": "rag_knowledge", "citations": citations})
                )
                db.add(asst_msg)
                db.commit()
                db.refresh(asst_msg)
                return {
                    "conversation_id": conv.id,
                    "message_id": asst_msg.id,
                    "response": response_text,
                    "intent": "rag_knowledge",
                    "citations": citations,
                    "audio_base64": None,
                    "emotional_support": False,
                    "model_used": llm_res["model"]
                }

            elif command == "/coping":
                coping_text = (
                    "### 🌿 Calming Grounding Exercise (5-4-3-2-1)\n\n"
                    "Take a slow, deep breath in... and gently exhale.\n\n"
                    "1. **5 things you can see**: Look around and notice 5 specific shapes or colors.\n"
                    "2. **4 things you can touch**: Notice the feeling of your chair, desk, or clothes.\n"
                    "3. **3 things you can hear**: Listen for ambient sounds near or far.\n"
                    "4. **2 things you can smell**: Notice any scent in the air.\n"
                    "5. **1 thing you are grateful for**: Bring to mind one simple positive thought.\n\n"
                    "*(You are in a safe space. Take all the time you need.)*"
                )
                asst_msg = Message(
                    conversation_id=conv.id,
                    message_role="assistant",
                    message_content=coping_text,
                    modality="text",
                    metadata_json=json.dumps({"intent": "emotional_support"})
                )
                db.add(asst_msg)
                db.commit()
                db.refresh(asst_msg)
                return {
                    "conversation_id": conv.id,
                    "message_id": asst_msg.id,
                    "response": coping_text,
                    "intent": "emotional_support",
                    "citations": [],
                    "audio_base64": None,
                    "emotional_support": True,
                    "model_used": "wellness-engine"
                }

            elif command == "/model":
                info_text = (
                    "### 🤖 Specialized Multi-Model AI Roster\n\n"
                    "- 💻 **Code & Software Engineering**: `Claude 3.5 Sonnet` *(Anthropic Code Architecture)*\n"
                    "- 📊 **Presentations & Slide Decks**: `Canva AI Engine` *(16:9 Widescreen & Canva Cloud Sync)*\n"
                    "- 🍌 **Image & Visual Creation**: `Nano Banana AI 2.1` *(High-Res Visual Studio)*\n"
                    "- 📑 **Document Analysis & PDF Output**: `PyMuPDF & Chroma Vector DB`\n"
                    "- 💬 **Chat & Emotional Wellness**: `Groq Qwen 3.8 / Gemini 2.5`\n"
                    "- 🗄️ **Database Persistence**: `MySQL 8.0` (Active on port 3306)"
                )
                asst_msg = Message(
                    conversation_id=conv.id,
                    message_role="assistant",
                    message_content=info_text,
                    modality="text",
                    metadata_json=json.dumps({"intent": "system_info"})
                )
                db.add(asst_msg)
                db.commit()
                db.refresh(asst_msg)
                return {
                    "conversation_id": conv.id,
                    "message_id": asst_msg.id,
                    "response": info_text,
                    "intent": "system_info",
                    "citations": [],
                    "audio_base64": None,
                    "emotional_support": False,
                    "model_used": "multi-model-router"
                }

        # 6. Check Image, Presentation, or Document Creation Intent
        is_gen, gen_type, subject = generator_service.detect_generation_intent(message_text)
        if is_gen:
            if gen_type == "presentation":
                intent = "presentation_generation"
                slide_prompt = (
                    f"Create a structured, 5-slide executive presentation outline about '{subject}'.\n"
                    "Format strictly as:\n"
                    "# Slide 1: Title\n[Subtitle]\n\n"
                    "# Slide 2: Problem & Market Need\n- point 1\n- point 2\n- point 3\n\n"
                    "# Slide 3: Core Solution & Value Proposition\n- point 1\n- point 2\n- point 3\n\n"
                    "# Slide 4: Key Metrics & Impact\n- point 1\n- point 2\n- point 3\n\n"
                    "# Slide 5: Strategic Roadmap & Next Steps\n- point 1\n- point 2\n- point 3"
                )
                llm_res = llm_service.generate_chat_response(
                    messages=[{"role": "user", "content": slide_prompt}],
                    system_prompt="You are a premier executive presentation designer specializing in Canva slide decks."
                )
                gen_res = generator_service.generate_canva_presentation(subject, llm_res["text"])
                response_text = gen_res["message"]
                db_gen_meta = {k: v for k, v in gen_res.items() if k not in ("data_uri", "file_bytes_b64")}
                metadata = {
                    "intent": intent,
                    "generated_file": db_gen_meta,
                    "model": "Canva AI Engine",
                    "specialist": "Canva AI (Presentation Specialist)"
                }
                asst_msg = Message(
                    conversation_id=conv.id,
                    message_role="assistant",
                    message_content=response_text,
                    modality="presentation",
                    metadata_json=json.dumps(metadata)
                )
                db.add(asst_msg)
                db.commit()
                db.refresh(asst_msg)
                return {
                    "conversation_id": conv.id,
                    "message_id": asst_msg.id,
                    "response": response_text,
                    "intent": intent,
                    "citations": [],
                    "audio_base64": None,
                    "emotional_support": False,
                    "model_used": "Canva AI Engine",
                    "specialist": "Canva AI (Presentation Specialist)",
                    "generated_file": gen_res
                }

            elif gen_type == "image":
                intent = "image_generation"
                gen_res = generator_service.generate_image(subject)
                response_text = gen_res["message"]
                
                db_gen_meta = {k: v for k, v in gen_res.items() if k not in ("data_uri", "file_bytes_b64")}
                metadata = {
                    "intent": intent,
                    "generated_file": db_gen_meta,
                    "model": "Nano Banana AI 2.1",
                    "specialist": "Nano Banana AI (Visual Studio)"
                }
                asst_msg = Message(
                    conversation_id=conv.id,
                    message_role="assistant",
                    message_content=response_text,
                    modality="image",
                    metadata_json=json.dumps(metadata)
                )
                db.add(asst_msg)
                db.commit()
                db.refresh(asst_msg)

                return {
                    "conversation_id": conv.id,
                    "message_id": asst_msg.id,
                    "response": response_text,
                    "intent": intent,
                    "citations": [],
                    "audio_base64": None,
                    "emotional_support": False,
                    "model_used": "Nano Banana AI 2.1",
                    "specialist": "Nano Banana AI (Visual Studio)",
                    "generated_file": gen_res
                }

            elif gen_type == "pdf":
                intent = "document_generation"
                doc_chunks = rag_service.retrieve_relevant_chunks(subject, top_k=4)
                sys_prompt = "You are a professional technical writer and document creator."
                if doc_chunks:
                    rag_ctx, _ = rag_service.build_grounded_system_prompt(doc_chunks)
                    sys_prompt = f"{rag_ctx}\n\nYou are writing an executive document based on the knowledge provided."

                doc_prompt = (
                    f"Write a structured, comprehensive document about '{subject}' "
                    "with clear section headings (# Heading), key facts, bullet points (- point), detailed explanations, and a strategic conclusion. "
                    "Do not use conversational filler."
                )
                llm_res = llm_service.generate_chat_response(
                    messages=[{"role": "user", "content": doc_prompt}],
                    system_prompt=sys_prompt
                )
                doc_content = llm_res["text"]
                gen_res = generator_service.generate_pdf_document(subject, doc_content)
                response_text = gen_res["message"]
                
                db_gen_meta = {k: v for k, v in gen_res.items() if k not in ("data_uri", "file_bytes_b64")}
                metadata = {
                    "intent": intent,
                    "generated_file": db_gen_meta,
                    "model": llm_res["model"]
                }
                asst_msg = Message(
                    conversation_id=conv.id,
                    message_role="assistant",
                    message_content=response_text,
                    modality="document",
                    metadata_json=json.dumps(metadata)
                )
                db.add(asst_msg)
                db.commit()
                db.refresh(asst_msg)

                return {
                    "conversation_id": conv.id,
                    "message_id": asst_msg.id,
                    "response": response_text,
                    "intent": intent,
                    "citations": [],
                    "audio_base64": None,
                    "emotional_support": False,
                    "model_used": llm_res["model"],
                    "specialist": "JIVAN PDF Document Studio",
                    "generated_file": gen_res
                }

        # 7. Check Specialized Coding Route (Claude 3.5 Sonnet)
        if is_coding_request(message_text):
            intent = "code_generation"
            code_res = llm_service.generate_code_response(formatted_messages)
            response_text = code_res["text"]
            model_name = code_res["model"]
            specialist = code_res.get("specialist", "Claude 3.5 Sonnet (Coding Specialist)")

            metadata = {
                "intent": intent,
                "model": model_name,
                "specialist": specialist,
                "citations": []
            }
            asst_msg = Message(
                conversation_id=conv.id,
                message_role="assistant",
                message_content=response_text,
                modality="text",
                metadata_json=json.dumps(metadata)
            )
            db.add(asst_msg)
            db.commit()
            db.refresh(asst_msg)

            return {
                "conversation_id": conv.id,
                "message_id": asst_msg.id,
                "response": response_text,
                "intent": intent,
                "citations": [],
                "audio_base64": None,
                "emotional_support": False,
                "model_used": model_name,
                "specialist": specialist
            }

        # 8. Intent Classification & Route Determination (RAG, Emotion, General)
        is_emotional = False
        emotional_category = "neutral"
        citations = []
        system_prompt = "You are a helpful, respectful, and intelligent AI companion."
        intent = "general_chat"

        # Check Emotional State
        if enable_emotional_support:
            is_emotional, emotional_category, emo_ctx = emotional_support_service.detect_emotional_state(message_text)
            if is_emotional:
                intent = "emotional_support"
                system_prompt = emotional_support_service.build_emotional_system_prompt(emotional_category)

        # Check RAG Document Retrieval if applicable
        if enable_rag and not is_emotional:
            chunks = rag_service.retrieve_relevant_chunks(message_text)
            if chunks:
                intent = "rag_knowledge"
                rag_prompt, citations = rag_service.build_grounded_system_prompt(chunks)
                system_prompt = rag_prompt

        # 9. Generate Response via LLM
        generation_result = llm_service.generate_chat_response(
            messages=formatted_messages,
            system_prompt=system_prompt
        )
        response_text = generation_result["text"]
        model_name = generation_result["model"]

        # Append medical disclaimer if emotional support was rendered
        if is_emotional:
            response_text = safety_service.append_disclaimer_if_needed(response_text, is_emotional=True)

        # 10. Persist Assistant Response in MySQL
        metadata = {
            "intent": intent,
            "citations": citations,
            "emotional_category": emotional_category if is_emotional else None,
            "model": model_name
        }
        asst_msg = Message(
            conversation_id=conv.id,
            message_role="assistant",
            message_content=response_text,
            modality="text",
            metadata_json=json.dumps(metadata)
        )
        db.add(asst_msg)
        db.commit()
        db.refresh(asst_msg)

        # 11. Optional TTS Audio
        audio_data = multimodal_service.generate_speech(response_text) if enable_tts else None

        return {
            "conversation_id": conv.id,
            "message_id": asst_msg.id,
            "response": response_text,
            "intent": intent,
            "citations": citations,
            "audio_base64": audio_data,
            "emotional_support": is_emotional,
            "model_used": model_name,
            "specialist": "JIVAN Knowledge & RAG Engine" if intent == "rag_knowledge" else None
        }

chat_service = ChatService()
