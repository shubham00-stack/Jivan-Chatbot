@echo off
cd /d "%~dp0"
echo ==============================================================
echo  Launching Multimodal AI Chatbot (FastAPI + Streamlit)
echo ==============================================================

set "PYTHON_EXE=C:\Users\shubh\AppData\Local\Programs\Python\Python314\python.exe"
if not exist "%PYTHON_EXE%" (
    set "PYTHON_EXE=python"
)

"%PYTHON_EXE%" app.py
