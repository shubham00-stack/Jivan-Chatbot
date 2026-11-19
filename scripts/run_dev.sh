#!/usr/bin/env bash
set -e

echo "=============================================================="
echo " Launching Multimodal AI Chatbot (FastAPI + Streamlit)"
echo "=============================================================="

# Start backend in background
uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload &
BACKEND_PID=$!

echo "Backend started with PID $BACKEND_PID. Waiting 3 seconds..."
sleep 3

# Start Streamlit frontend
streamlit run frontend/streamlit_app.py --server.port 8501

# Clean up background process on exit
kill $BACKEND_PID

