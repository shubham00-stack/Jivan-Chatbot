"""
JIVAN Enterprise AI Assistant - Root Entrypoint for Streamlit Community Cloud
"""
import sys
import os
from pathlib import Path

# Ensure root workspace is at the top of sys.path
root_dir = str(Path(__file__).resolve().parent)
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

# Execute the main Streamlit application
from frontend.streamlit_app import *
