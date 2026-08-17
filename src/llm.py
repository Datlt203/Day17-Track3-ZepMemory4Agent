"""Thin Gemini wrapper for the demo UI chat reply.

This is the ONLY place the lab calls a generative LLM. Benchmark scoring never
uses an LLM (see LAB.md): retrieval evidence is graded deterministically. Here
Gemini only turns retrieved memory context into a grounded assistant reply so
the mini-product feels real.

Default model: gemini-2.5-flash-lite (override with GEMINI_MODEL).
"""

from __future__ import annotations

import time
from typing import Any

from .config import settings

SYSTEM_INSTRUCTION = (
    "You are the assistant of a personal memory agent for VinUni Lab 17. "
    "Answer the user grounded ONLY in the retrieved memory context provided. "
    "If the context does not contain the answer, say so plainly instead of "
    "inventing facts. Do not repeat or quote the user's long prompt. "
    "Give a complete, practical answer with short sections and cite the "
    "concrete markers/ids you used. "
    "You may reply in the user's language (Vietnamese or English)."
)

RETRYABLE_STATUS_CODES = {429, 500, 502, 503, 504}


def gemini_available() -> bool:
    """True when a key is configured. UI uses this to show status."""
    return bool(settings.gemini_api_key)


def _to_contents(history: list[dict[str, str]]) -> list[dict[str, Any]]:
    """Map chat history to google-genai `contents` turns.

    Roles: user -> "user", everything else (assistant/model) -> "model".
    """
    contents: list[dict[str, Any]] = []
    for msg in history:
        role = "user" if msg.get("role") == "user" else "model"
        text = msg.get("content", "")
        if not text:
            continue
        contents.append({"role": role, "parts": [{"text": text}]})
    return contents


def _status_code(exc: Exception) -> int | None:
    for attr in ("status_code", "code"):
        value = getattr(exc, attr, None)
        if isinstance(value, int):
            return value

    response = getattr(exc, "response", None)
    value = getattr(response, "status_code", None)
    if isinstance(value, int):
        return value
    return None


def _is_retryable_error(exc: Exception) -> bool:
    code = _status_code(exc)
    if code in RETRYABLE_STATUS_CODES:
        return True

    text = f"{type(exc).__name__}: {exc}".casefold()
    retryable_markers = (
        "429",
        "500",
        "502",
        "503",
        "504",
        "unavailable",
        "overloaded",
        "rate limit",
        "temporarily",
        "timeout",
    )
    return any(marker in text for marker in retryable_markers)


def generate_reply(
    memory_context: str,
    history: list[dict[str, str]],
    user_message: str,
    *,
    model: str | None = None,
    retries: int = 3,
    base_delay: float = 1.0,
) -> str:
    """Generate a grounded assistant reply with Gemini.

    Retries transient SDK/network errors with exponential backoff, then lets the
    final error bubble up so the UI can fall back to retrieved context.
    `history` should include the latest user turn or not; `user_message` is
    appended as the final user turn regardless.
    """
    if not settings.gemini_api_key:
        raise RuntimeError(
            "GEMINI_API_KEY is missing. Copy .env.example to .env and add a "
            "Google AI Studio key to enable chat replies."
        )

    # Lazy import so the rest of the package works without google-genai installed
    # (tests, report generation, retrieval benchmarks never need it).
    from google import genai
    from google.genai import types

    client = genai.Client(api_key=settings.gemini_api_key)
    model_name = model or settings.gemini_model

    grounding = (
        "Retrieved memory context for this turn:\n"
        "-------------------------------------\n"
        f"{memory_context.strip() or '(no memory retrieved)'}\n"
        "-------------------------------------\n\n"
        f"User message: {user_message}"
    )

    contents = _to_contents(history)
    contents.append({"role": "user", "parts": [{"text": grounding}]})

    attempts = max(1, retries)
    last_error: Exception | None = None
    for attempt in range(attempts):
        try:
            response = client.models.generate_content(
                model=model_name,
                contents=contents,
                config=types.GenerateContentConfig(
                    system_instruction=SYSTEM_INSTRUCTION,
                    temperature=0.3,
                    max_output_tokens=settings.gemini_max_output_tokens,
                ),
            )
            return (getattr(response, "text", "") or "").strip()
        except Exception as exc:
            last_error = exc
            if attempt == attempts - 1 or not _is_retryable_error(exc):
                raise
            time.sleep(base_delay * (2**attempt))

    if last_error:
        raise last_error
    return ""
