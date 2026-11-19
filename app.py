import sys
import subprocess
import os
import time
import webbrowser
import signal

def find_working_python():
    """Finds the Python interpreter that contains the installed dependencies."""
    # 1. Check current python
    try:
        import uvicorn
        import streamlit
        return sys.executable
    except ImportError:
        pass

    # 2. Check Python 3.14 where all dependencies are verified
    py314 = r"C:\Users\shubh\AppData\Local\Programs\Python\Python314\python.exe"
    if os.path.exists(py314):
        return py314

    # 3. Check Local AppData variations
    local_app_data = os.environ.get("LOCALAPPDATA", "")
    if local_app_data:
        candidate = os.path.join(local_app_data, "Programs", "Python", "Python314", "python.exe")
        if os.path.exists(candidate):
            return candidate

    return sys.executable

PYTHON_EXE = find_working_python()

def run_backend(standalone=False):
    print("=" * 60)
    print("🚀 Starting FastAPI Backend on http://localhost:8000 ...")
    print(f"Using Python: {PYTHON_EXE}")
    print("=" * 60)
    cmd = [PYTHON_EXE, "-m", "uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
    if standalone:
        subprocess.run(cmd)
    else:
        return subprocess.Popen(cmd)

def run_frontend(standalone=False):
    print("=" * 60)
    print("🌟 Starting Streamlit Frontend on http://localhost:8501 ...")
    print(f"Using Python: {PYTHON_EXE}")
    print("=" * 60)
    cmd = [PYTHON_EXE, "-m", "streamlit", "run", "frontend/streamlit_app.py", "--server.port", "8501", "--server.address", "0.0.0.0", "--server.headless", "true"]
    if standalone:
        subprocess.run(cmd)
    else:
        return subprocess.Popen(cmd)

def run_both():
    # Change directory to project root
    project_root = os.path.dirname(os.path.abspath(__file__))
    os.chdir(project_root)

    print("=" * 65)
    print("🤖 Multimodal AI Chatbot (FastAPI Backend + Streamlit Web UI)")
    print(f"Working Directory: {project_root}")
    print(f"Python Runtime:    {PYTHON_EXE}")
    print("=" * 65)

    # 1. Start FastAPI Backend in background
    backend_proc = run_backend(standalone=False)
    time.sleep(3)

    # 2. Start Streamlit Frontend in background
    frontend_proc = run_frontend(standalone=False)
    time.sleep(2)

    print("\n" + "=" * 65)
    print("✅ All services are LIVE!")
    print("👉 Frontend (Web UI): http://localhost:8501")
    print("👉 Backend API:       http://localhost:8000")
    print("👉 API Documentation: http://localhost:8000/docs")
    print("Press Ctrl+C to stop all services.")
    print("=" * 65 + "\n")

    try:
        webbrowser.open("http://localhost:8501")
    except Exception:
        pass

    try:
        while True:
            time.sleep(1)
            if backend_proc.poll() is not None:
                print("Backend terminated.")
                break
            if frontend_proc.poll() is not None:
                print("Frontend terminated.")
                break
    except KeyboardInterrupt:
        print("\nStopping services...")
    finally:
        if backend_proc and backend_proc.poll() is None:
            backend_proc.terminate()
        if frontend_proc and frontend_proc.poll() is None:
            frontend_proc.terminate()
        print("All services stopped.")

def main():
    if len(sys.argv) > 1:
        cmd = sys.argv[1].lower()
        if cmd == "backend":
            run_backend(standalone=True)
            return
        elif cmd == "frontend":
            run_frontend(standalone=True)
            return
        elif cmd in ("both", "all", "start"):
            run_both()
            return

    # Default action when running `python app.py`: launch both!
    run_both()

if __name__ == "__main__":
    main()
