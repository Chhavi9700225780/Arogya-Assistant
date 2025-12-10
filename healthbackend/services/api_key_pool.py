import os
import time
import threading
from typing import List, Dict

from dotenv import load_dotenv
load_dotenv()


# Read all keys from env: GOOGLE_API_KEY=key1,key2,key3
_keys: List[str] = [
    k.strip()
    for k in os.getenv("GOOGLE_API_KEY", "").split(",")
    if k.strip()
]

# For each key, track when it becomes usable again (epoch seconds)
_key_state: Dict[str, float] = {k: 0.0 for k in _keys}

# Lock to keep operations thread-safe
_lock = threading.Lock()

# How long to disable a key after quota error (seconds)
COOLDOWN_SECONDS = 3600  # 1 hour


def get_next_key() -> str:
    """Return the next available API key, skipping keys in cooldown."""
    with _lock:
        if not _keys:
            raise RuntimeError("No GOOGLE_API_KEY configured")

        now = time.time()
        available = [k for k in _keys if _key_state.get(k, 0) <= now]
        if not available:
            raise RuntimeError(
                "All Gemini API keys are currently in cooldown due to quota limits."
            )

        # Simple round-robin: take first available, move it to the end
        key = available[0]
        _keys.remove(key)
        _keys.append(key)
        return key


def mark_key_quota_exceeded(key: str) -> None:
    """Mark a key as temporarily disabled because quota was exceeded."""
    with _lock:
        if key in _key_state:
            _key_state[key] = time.time() + COOLDOWN_SECONDS
