"""Minimal NVIDIA NIM HTTP client for chat completions and embeddings."""

from typing import Literal

import requests

from backend.app.config import (
    NVIDIA_API_KEY,
    NVIDIA_BASE_URL,
    NVIDIA_CHAT_MODEL,
    NVIDIA_EMBEDDING_MODEL,
    NVIDIA_TIMEOUT_SECONDS,
)


def _headers() -> dict[str, str]:
    """Build authenticated headers without ever logging the API key."""
    if not NVIDIA_API_KEY:
        raise RuntimeError("NVIDIA_API_KEY is not configured. Add it to your .env file.")
    return {"Authorization": f"Bearer {NVIDIA_API_KEY}", "Content-Type": "application/json"}


def _post(path: str, payload: dict) -> dict:
    """Call NIM once and translate upstream failures into actionable API errors."""
    try:
        response = requests.post(f"{NVIDIA_BASE_URL}{path}", headers=_headers(), json=payload, timeout=NVIDIA_TIMEOUT_SECONDS)
    except requests.RequestException as error:
        raise RuntimeError("NVIDIA NIM is unavailable. Please try again shortly.") from error

    if response.status_code == 401:
        raise RuntimeError("NVIDIA API authentication failed. Check NVIDIA_API_KEY.")
    if response.status_code == 429:
        raise RuntimeError("NVIDIA API rate limit reached. Please try again shortly.")
    if not response.ok:
        raise RuntimeError("NVIDIA NIM returned an error. Please try again shortly.")
    try:
        return response.json()
    except ValueError as error:
        raise RuntimeError("NVIDIA NIM returned an invalid response. Please try again shortly.") from error


def embed_texts(texts: list[str], input_type: Literal["passage", "query"]) -> list[list[float]]:
    """Embed a batch using NIM's required passage/query retrieval modes."""
    if not texts:
        return []
    data = _post(
        "/embeddings",
        {"model": NVIDIA_EMBEDDING_MODEL, "input": texts, "input_type": input_type, "encoding_format": "float"},
    )
    # NIM includes indices, so sort defensively before returning vectors to Chroma.
    return [item["embedding"] for item in sorted(data["data"], key=lambda item: item["index"])]


def generate_answer(system_prompt: str, question: str) -> str:
    """Generate a concise grounded answer from the configured NIM chat model."""
    data = _post(
        "/chat/completions",
        {
            "model": NVIDIA_CHAT_MODEL,
            "temperature": 0.2,
            "max_tokens": 700,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": question},
            ],
        },
    )
    return (data.get("choices") or [{}])[0].get("message", {}).get("content", "").strip()
