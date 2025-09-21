import json
import requests
from typing import Dict, List
from config import OLLAMA_BASE, OLLAMA_MODEL


def _ollama_generate(prompt: str) -> str:
    url = f"{OLLAMA_BASE}/api/generate"
    payload = {"model": OLLAMA_MODEL, "prompt": prompt, "stream": False}
    r = requests.post(url, json=payload, timeout=600)
    r.raise_for_status()
    data = r.json()
    return (data.get("response") or "").strip()


def summarize_and_extract(transcript: str) -> Dict[str, List[str] | str]:
    system = (
        "You are a helpful meeting analyst. Given a transcript, produce STRICT JSON with keys: "
        "overview (string), key_topics (string[]), decisions (string[]), action_items (string[]), "
        "risks (string[]), vibe (string). Be concise and use short bullet-like strings."
    )

    # Avoid nested triple-quotes; keep it simple so Python's parser is happy.
    clipped = transcript[:20000]
    prompt = (
        f"{system}\n\n"
        f"TRANSCRIPT:\n"
        f"{clipped}\n\n"
        f"Return STRICT JSON only, no commentary, no code fences."
    )

    resp = _ollama_generate(prompt)

    # Try to parse JSON; if model returns non-JSON, fall back safely.
    try:
        obj = json.loads(resp)
    except Exception:
        obj = {
            "overview": resp[:500],
            "key_topics": [],
            "decisions": [],
            "action_items": [],
            "risks": [],
            "vibe": "neutral",
        }

    # sanity fill
    obj.setdefault("overview", "")
    obj.setdefault("key_topics", [])
    obj.setdefault("decisions", [])
    obj.setdefault("action_items", [])
    obj.setdefault("risks", [])
    obj.setdefault("vibe", "neutral")
    return obj
