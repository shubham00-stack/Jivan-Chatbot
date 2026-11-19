import os
import requests
from dotenv import load_dotenv

load_dotenv()
groq_key = os.environ.get("GROQ_API_KEY", "")

headers = {
    "Authorization": f"Bearer {groq_key}",
    "Content-Type": "application/json"
}

payload = {
    "model": "qwen/qwen3.8-27b",
    "messages": [{"role": "user", "content": "Write a python for loop example"}],
    "temperature": 0.5
}

try:
    print("Sending request to Groq API...", flush=True)
    resp = requests.post("https://api.groq.com/openai/v1/chat/completions", headers=headers, json=payload, timeout=10)
    print("Status:", resp.status_code)
    print("Response:", resp.json())
except Exception as e:
    print("Error:", e)
