import os
from google import genai
from dotenv import load_dotenv

load_dotenv()
gemini_key = os.environ.get("GEMINI_API_KEY", "")

client = genai.Client(api_key=gemini_key)

candidate_models = [
    "gemini-2.5-flash",
    "gemini-2.0-flash"
]

for m in candidate_models:
    try:
        print(f"Testing model {m}...", flush=True)
        resp = client.models.generate_content(model=m, contents="Say hello in one word")
        print(f"--> SUCCESS with {m}! Response: {resp.text.strip()}", flush=True)
        break
    except Exception as e:
        print(f"--> Failed {m}: {e}", flush=True)
