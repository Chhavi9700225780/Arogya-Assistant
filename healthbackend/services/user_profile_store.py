import json
import os

FILE = "healthbackend/storage/user_profiles.json"


def _load():
    if not os.path.exists(FILE):
        return {}
    with open(FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def _save(data):
    os.makedirs(os.path.dirname(FILE), exist_ok=True)
    with open(FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


def save_profile(user_id: str, profile: dict):
    data = _load()
    data[user_id] = profile
    _save(data)


def get_profile(user_id: str) -> dict:
    return _load().get(user_id, {})
