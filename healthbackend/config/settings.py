import os
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("API_KEY")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
MODEL_NAME = os.getenv("MODEL_NAME", "gemini-2.5-flash")

if not API_KEY:
    raise RuntimeError("API_KEY not found in environment")

if not GOOGLE_API_KEY:
    raise RuntimeError("GOOGLE_API_KEY not found in environment")
