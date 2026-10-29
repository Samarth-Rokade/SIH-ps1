"""Thin client for a local Ollama server (stdlib only, no extra dependency).

The assistant uses this only to *phrase* an answer from database facts it has
already retrieved; if Ollama isn't running, callers fall back to the built-in
grounded answer, so the feature degrades instead of failing.
"""
from __future__ import annotations

import json
import os
import time
import urllib.error
import urllib.request

from app.utils.constants import (
    DEFAULT_OLLAMA_MODEL,
    DEFAULT_OLLAMA_URL,
    OLLAMA_MODEL_ENV,
    OLLAMA_URL_ENV,
)

AVAILABILITY_TTL_SECONDS = 15
GENERATE_TIMEOUT_SECONDS = 60

_availability_cache: tuple[float, bool] = (0.0, False)


def base_url() -> str:
    return os.environ.get(OLLAMA_URL_ENV, DEFAULT_OLLAMA_URL).rstrip("/")


def model_name() -> str:
    return os.environ.get(OLLAMA_MODEL_ENV, DEFAULT_OLLAMA_MODEL)


def is_available() -> bool:
    """Cached reachability + model-installed check (a 1s probe at most every 15s)."""
    global _availability_cache
    checked_at, available = _availability_cache
    if time.monotonic() - checked_at < AVAILABILITY_TTL_SECONDS:
        return available
    try:
        with urllib.request.urlopen(f"{base_url()}/api/tags", timeout=1.0) as resp:
            names = [m.get("name", "") for m in json.load(resp).get("models", [])]
        wanted = model_name().split(":")[0]
        available = any(n.split(":")[0] == wanted for n in names)
    except (urllib.error.URLError, TimeoutError, OSError, ValueError):
        available = False
    _availability_cache = (time.monotonic(), available)
    return available


def generate(system: str, prompt: str) -> str | None:
    """Returns the model's reply, or None if the call fails for any reason."""
    if not is_available():
        return None
    body = json.dumps(
        {
            "model": model_name(),
            "stream": False,
            "options": {"temperature": 0.2},
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": prompt},
            ],
        }
    ).encode()
    request = urllib.request.Request(
        f"{base_url()}/api/chat", data=body, headers={"Content-Type": "application/json"}
    )
    try:
        with urllib.request.urlopen(request, timeout=GENERATE_TIMEOUT_SECONDS) as resp:
            reply = json.load(resp).get("message", {}).get("content", "").strip()
        return reply or None
    except (urllib.error.URLError, TimeoutError, OSError, ValueError):
        return None
