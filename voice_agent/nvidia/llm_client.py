"""
llm_client.py
-------------
Nemotron LLM via NVIDIA OpenAI-compatible API.
"""

from __future__ import annotations

from openai import OpenAI

from config import (
    NEMOTRON_LLM_MODEL,
    NVIDIA_API_KEY,
    NVIDIA_LLM_BASE_URL,
    SYSTEM_PROMPT,
)

_client: OpenAI | None = None


def _get_client() -> OpenAI:
    global _client
    if _client is None:
        if not NVIDIA_API_KEY:
            raise RuntimeError("NVIDIA_API_KEY not set")
        _client = OpenAI(
            base_url=NVIDIA_LLM_BASE_URL,
            api_key=NVIDIA_API_KEY,
        )
    return _client


def chat(history: list[dict], extra_system: str = "") -> dict:
    """
    Send conversation history to Nemotron LLM.
    history: [{"role": "user"|"assistant", "content": str}, ...]
    Returns: {"text": str, "backend": "nemotron", "error": str|None}
    """
    try:
        client = _get_client()
        system = SYSTEM_PROMPT
        if extra_system:
            system = f"{SYSTEM_PROMPT}\n\n{extra_system}"

        messages = [{"role": "system", "content": system}] + history
        response = client.chat.completions.create(
            model=NEMOTRON_LLM_MODEL,
            messages=messages,
            max_tokens=512,
            temperature=0.7,
        )
        text = response.choices[0].message.content or ""
        return {"text": text.strip(), "backend": "nemotron", "error": None}

    except Exception as exc:
        err = str(exc)
        if "429" in err or "rate" in err.lower():
            err = "Rate limit reached (~40 RPM free tier). Please wait a moment."
        return {"text": "", "backend": None, "error": err}
