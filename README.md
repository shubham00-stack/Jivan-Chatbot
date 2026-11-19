# 🍃 JIVAN — Enterprise Multimodal AI Assistant

[![FastAPI](https://img.shields.io/badge/FastAPI-0.110+-009688.svg?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.35+-FF4B4B.svg?logo=streamlit&logoColor=white)](https://streamlit.io)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-blue.svg?logo=python&logoColor=white)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

A production-ready Enterprise Multimodal AI Assistant featuring a **NotebookLM-style workspace**, **Specialized Multi-Model Routing**, **Retrieval-Augmented Generation (RAG)**, and **Personal Emotional Wellness Guardrails**.

---

## 🌟 Specialized Multi-Model AI Roster

JIVAN orchestrates dedicated AI models mapped to their domain strengths:

| Specialist Role | Powered By | Capabilities & Trigger Commands |
| :--- | :--- | :--- |
| 💻 **Code & Software Architecture** | **Claude 3.5 Sonnet** | Clean algorithms, full scripts, debugging, refactoring (`/code <prompt>`) |
| 📊 **Presentations & Slide Decks** | **Canva AI Engine** | Builds 16:9 widescreen `.pptx` decks with instant download & Canva Cloud link (`/slides <topic>`) |
| 🍌 **Image & Visual Generation** | **Nano Banana AI 2.1** | High-definition visual synthesis with multi-tier failover & generative art cards (`/image <prompt>`) |
| 📑 **Document Analysis & PDF Output** | **PyMuPDF & Chroma RAG** | Vector retrieval with grounded source citations & executive PDF export (`/pdf <topic>`) |
| 💬 **Conversational & Wellness Engine** | **Groq Qwen 3.8 / Gemini 2.5** | Low-latency chat, crisis intervention hotline (`988`), and calming exercises (`/coping`) |

---

## 1. Project Capabilities

1. **Multimodal Interaction**:
   - **Text**: Natural multi-turn conversational chat with persistent context.
   - **Images**: Visual scene understanding and analysis via vision-capable models (e.g. Gemini 2.5 Flash / GPT-4o).
   - **Documents**: Upload PDF and TXT files, parsed, chunked, and indexed into a local semantic vector store.
   - **Audio**: Upload voice recordings or record directly in-browser, automatically transcribe via Speech-to-Text (Groq Whisper), and optionally generate voice audio responses via Text-to-Speech (TTS).

2. **Knowledge-Grounded Retrieval (RAG)**:
   - PyMuPDF text extraction.
   - Recursive character chunking (configurable chunk size and overlap).
   - High-performance vector embeddings and similarity search.
   - Strict context sandboxing (`<untrusted_knowledge_base>`) to prevent hallucination and prompt injection from untrusted files.
   - Grounded citations citing document names and chunk indices.

3. **Personal Emotional Support & Crisis Sentinel**:
   - Analyzes user emotional state (anxiety, overwhelm, loneliness, sadness, grief).
   - Employs an empathetic, respectful, non-judgmental conversational persona.
   - Provides gentle wellness exercises (e.g., Box Breathing, 5-4-3-2-1 Grounding).
   - **Crisis Guardrail**: Deterministic interception of self-harm, suicidal ideation, or abuse inquiries, immediately referring users to 24/7 emergency helplines (US/Canada `988`, Crisis Text Line `741741`, `findahelpline.com`).
   - Clear non-clinical disclaimer: never diagnoses conditions, prescribes medication, or replaces professional therapy.

4. **Secure Communication Portal**:
   - Regex-based prompt injection and jailbreak detector.
   - Strict MIME type and file size limits (15MB max).
   - Input sanitization (strips null bytes, control characters, and unsafe HTML tags).
   - In-memory rate limiting (60 requests/minute per client IP).
   - CORS restrictions and safe error handling without internal stack trace leakage.
   - Mechanism to permanently delete conversation history and indexed documents.

---

## 2. Technology Stack

- **Backend**: Python 3.10+, FastAPI, Uvicorn, Pydantic v2.
- **Frontend**: Streamlit.
- **Database**: MySQL 8.0+ via SQLAlchemy ORM (with automatic fallback to SQLite for zero-setup local dev).
- **Vector Search**: Local vector store using Cosine Similarity on normalized dense embeddings.
- **AI Integration**: Modular adapter supporting Google Gemini (`google-genai`), OpenAI (`openai`), and offline intelligent fallback.
- **Document & Image Processing**: PyMuPDF (`pymupdf`), Pillow (`PIL`).
- **Audio & Speech**: `gTTS` (Text-to-Speech), Speech-to-Text (Whisper / SpeechRecognition API).
- **Testing**: `pytest`, `starlette.testclient`.

---

## 3. Architecture & Data Flow

```
Streamlit Frontend (Port 8501)
         |
         | HTTP REST (JSON / Multipart)
         v
FastAPI Backend Gateway (Port 8000)
    ├── Security Layer (Sanitization, Injection Shield, Rate Limiter, Crisis Sentinel)
    ├── Intent Router
    │     ├── Emotional Support Service
    │     ├── RAG Retrieval Service
    │     ├── Multimodal Processing (Vision & Speech)
    │     └── Core Conversational Engine
    │
    ├── Data Storage
    │     ├── MySQL Database (Conversations, Messages, Documents, Feedback)
    │     ├── Local Vector Store (/storage/vector_db/)
    │     └── Upload Staging (/storage/uploads/)
    │
    └── AI Provider Adapters (Google Gemini / OpenAI / Local Encoder)
```

---

## 4. Project Directory Structure

```
c:\ML\
├── app.py                         # Unified entrypoint helper
├── requirements.txt               # Pinned dependencies
├── .env.example                   # Environment variable template
├── .env                           # Local configuration
├── README.md                      # Complete system documentation
│
├── backend/
│   ├── main.py                    # FastAPI application initialization & middleware
│   ├── api/
│   │   ├── router.py              # Central API router
│   │   └── routes/
│   │       ├── chat.py            # Text, image, and audio chat endpoints
│   │       ├── documents.py       # Document upload, query, management
│   │       ├── conversations.py   # Conversation history CRUD
│   │       ├── feedback.py        # Thumbs up / down feedback collection
│   │       └── health.py          # Diagnostic & health check endpoint
│   ├── core/
│   │   ├── config.py              # Pydantic Settings & environment loader
│   │   ├── logging.py             # Structured logger
│   │   └── security.py            # Sanitization, rate limiter, guardrails
│   ├── database/
│   │   ├── connection.py          # SQLAlchemy engine, sessionmaker, fallback
│   │   ├── init_db.py             # Database creation script
│   │   └── schema.sql             # Pure MySQL DDL script
│   ├── models/
│   │   └── orm_models.py          # SQLAlchemy ORM model declarations
│   ├── schemas/
│   │   ├── chat_schema.py         # Request & response Pydantic models
│   │   ├── document_schema.py     # Document metadata & chunk models
│   │   └── feedback_schema.py     # Feedback request models
│   └── services/
│       ├── llm_service.py         # Modular LLM & Vision provider adapter
│       ├── chat_service.py        # Chat orchestration & history builder
│       ├── multimodal_service.py  # Image inspection & Speech (STT/TTS)
│       ├── emotional_support_service.py # Empathy & emotional tone analyzer
│       ├── rag_service.py         # RAG query, context grounding & citations
│       ├── document_service.py    # Document text extraction & ingestion
│       └── safety_service.py      # Crisis detection & prompt injection shield
│
├── frontend/
│   ├── streamlit_app.py           # Main Streamlit UI application
│   ├── components/
│   │   ├── sidebar.py             # Conversation list, doc manager, settings
│   │   ├── chat_view.py           # Message bubbles, markdown, audio player
│   │   └── media_inputs.py        # Image uploader, microphone/audio uploader
│   └── utils/
│       └── api_client.py          # Backend HTTP client communicating with FastAPI
│
├── rag/
│   ├── chunking.py                # Recursive character text splitter
│   ├── embeddings.py              # Modular dense embedding generator
│   └── vector_store.py            # Vector store index manager
│
├── storage/
│   ├── uploads/                   # Staged upload media directory
│   └── vector_db/                 # Serialized vector indices & metadata
│
├── tests/
│   ├── test_api.py                # FastAPI endpoint integration tests
│   ├── test_rag.py                # Document chunking & vector search tests
│   ├── test_safety.py             # Prompt injection & crisis sentinel tests
│   └── test_emotional.py          # Emotional tone & disclaimer verification
│
└── scripts/
    ├── init_mysql.py              # MySQL table initializer script
    ├── run_dev.bat                # Windows launch script
    └── run_dev.sh                 # Linux/Mac launch script
```

---

## 5. Local Setup & Installation

### Step 1: Clone or Open Workspace
Ensure your shell is positioned in the project directory:
```bash
cd c:\ML
```

### Step 2: Install Dependencies
Install all required Python packages using pip:
```bash
pip install -r requirements.txt
```

### Step 3: Configure Environment Variables
Copy `.env.example` to `.env`:
```bash
copy .env.example .env
```
Edit `.env` to configure your API keys and database credentials:
```env
# AI Providers (Google Gemini or OpenAI)
LLM_PROVIDER=gemini
GEMINI_API_KEY=your_gemini_api_key_here
GEMINI_MODEL=gemini-2.5-flash

# Database Configuration (MySQL with automatic SQLite fallback)
DATABASE_URL=mysql+pymysql://root:password@localhost:3306/multimodal_chatbot
SQLITE_FALLBACK_URL=sqlite:///./chatbot.db
```
*(Note: If no API keys are provided, the system seamlessly operates in offline development mode without failing.)*

### Step 4: Initialize the Database
To initialize tables in MySQL (or SQLite fallback):
```bash
python scripts/init_mysql.py
```
Or execute the pure MySQL DDL script directly in MySQL Workbench / CLI:
```bash
mysql -u root -p < backend/database/schema.sql
```

---

## 6. Running the Application

### Option A: Direct Windows Launcher
Double-click `run_project.bat` in the project root:
```cmd
.\run_project.bat
```

### Option B: Unified Python Launcher (Cross-Platform)
```bash
python app.py
```
This automatically binds to the verified Python environment, starts the FastAPI backend on port 8000, starts Streamlit on port 8501, and auto-opens your browser to `http://localhost:8501`.

### Option C: Manual Launch

1. **Start the FastAPI Backend** (Terminal 1):
```bash
python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
```
API Documentation will be accessible at: **`http://localhost:8000/docs`**

2. **Start the Streamlit Frontend** (Terminal 2):
```bash
python -m streamlit run frontend/streamlit_app.py --server.port 8501
```
The User Interface will open automatically at: **`http://localhost:8501`**

---

## 7. REST API Documentation (FastAPI)

Interactive Swagger UI documentation is available at `http://localhost:8000/docs`.

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/api/health` | System health check (DB, LLM, Vector Store status) |
| `POST` | `/api/chat` | Send text message (RAG & Emotional Support aware) |
| `POST` | `/api/chat/image` | Upload image + question for vision understanding |
| `POST` | `/api/chat/audio` | Upload audio voice message (STT + TTS playback) |
| `POST` | `/api/documents/upload` | Ingest and index PDF or TXT files into RAG store |
| `POST` | `/api/documents/query` | Direct semantic vector search against indexed documents |
| `GET` | `/api/documents` | List all indexed documents |
| `DELETE` | `/api/documents/{id}` | Delete document and its vector embeddings |
| `GET` | `/api/conversations` | List recent conversation sessions |
| `GET` | `/api/conversations/{id}`| Fetch full message history for a conversation |
| `DELETE` | `/api/conversations/{id}`| Permanently delete a conversation |
| `POST` | `/api/feedback` | Record user 👍 / 👎 feedback on assistant responses |

---

## 8. Running Automated Tests

Run the full automated test suite covering safety, emotional support, RAG, and FastAPI endpoints:
```bash
pytest -v
```

All 14 unit and integration tests will execute:
- `tests/test_api.py` (API health, chat, conversations, feedback, and security blocks)
- `tests/test_safety.py` (Prompt injection mitigation & crisis intervention hotline)
- `tests/test_emotional.py` (Emotional distress detection & coping suggestion delivery)
- `tests/test_rag.py` (Recursive chunking, dense embeddings, vector search)

---

## 9. Controlled Environment Notice & Medical Disclaimer

> **IMPORTANT**: This application is an MVP designed for controlled demonstration, research, and trusted development environments. It does not implement user authentication or enterprise RBAC.
>
> **HEALTHCARE DISCLAIMER**: The chatbot is an AI conversational agent, **NOT** a doctor, psychologist, or licensed therapist. It does not diagnose medical or psychological conditions, prescribe medication, or offer clinical treatments. If you or someone you know is in crisis or danger, please contact emergency services or call/text **988** (US/Canada Lifeline) immediately.

