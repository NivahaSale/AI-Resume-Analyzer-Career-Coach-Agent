from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any, Dict, List, TypedDict

from dotenv import load_dotenv
from groq import Groq

_BACKEND_DIR = Path(__file__).resolve().parents[1]
load_dotenv(dotenv_path=_BACKEND_DIR / ".env", override=False)


class ChatMessage(TypedDict):
    role: str  # "user" | "assistant"
    content: str


def _safe_json_object(content: str) -> Dict[str, Any]:
    try:
        parsed = json.loads(content)
    except json.JSONDecodeError as exc:
        raise ValueError("Model returned invalid JSON.") from exc
    if not isinstance(parsed, dict):
        raise ValueError("Model returned unexpected JSON shape.")
    return parsed


def _as_str_list(value: Any) -> List[str]:
    if not isinstance(value, list):
        return []
    out: List[str] = []
    for item in value:
        if isinstance(item, str) and item.strip():
            out.append(item.strip())
    return out


def generate_chat_reply(
    *,
    user_message: str,
    history: List[ChatMessage],
    resume_text: str | None,
    job_description: str | None,
) -> Dict[str, Any]:
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise ValueError("GROQ_API_KEY not found in environment variables")

    user_message = (user_message or "").strip()
    if not user_message:
        raise ValueError("Message is required.")

    # Keep only the last few turns to control token usage.
    trimmed_history = []
    for msg in history[-10:]:
        role = (msg.get("role") or "").strip()
        content = (msg.get("content") or "").strip()
        if role in {"user", "assistant"} and content:
            trimmed_history.append({"role": role, "content": content})

    client = Groq(api_key=api_key)
    model = "llama-3.3-70b-versatile"

    system_prompt = """
You are an AI resume coach and interview mentor.

You will be given:
- The user's resume text (if provided)
- An optional job description
- A short chat history

Return ONLY valid JSON in this exact shape:
{
  "answer": "string",
  "suggested_edits": ["string"],
  "next_actions": ["string"],
  "clarifying_questions": ["string"]
}

Rules:
- Be specific and actionable. Prefer rewrites, bullet improvements, and step-by-step guidance.
- Ground advice in the resume text and job description when provided.
- Keep each list item short (one idea per item).
- If resume text is missing, ask for it in clarifying_questions.
"""

    context_block = f"""
JOB_DESCRIPTION (optional):
{job_description or ""}

RESUME (optional):
{resume_text or ""}
""".strip()

    messages: List[Dict[str, str]] = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": context_block},
    ]
    messages.extend(trimmed_history)
    messages.append({"role": "user", "content": user_message})

    response = client.chat.completions.create(
        model=model,
        messages=messages,
        response_format={"type": "json_object"},
        temperature=0.4,
        max_tokens=900,
    )

    data = _safe_json_object(response.choices[0].message.content or "{}")
    answer = data.get("answer", "")
    if not isinstance(answer, str):
        answer = ""

    return {
        "answer": answer.strip(),
        "suggested_edits": _as_str_list(data.get("suggested_edits")),
        "next_actions": _as_str_list(data.get("next_actions")),
        "clarifying_questions": _as_str_list(data.get("clarifying_questions")),
    }


def parse_history_json(history_json: str | None) -> List[ChatMessage]:
    if not history_json:
        return []
    try:
        parsed = json.loads(history_json)
    except json.JSONDecodeError:
        raise ValueError("Invalid history format.")
    if not isinstance(parsed, list):
        raise ValueError("Invalid history format.")

    out: List[ChatMessage] = []
    for item in parsed:
        if not isinstance(item, dict):
            continue
        role = item.get("role")
        content = item.get("content")
        if role in {"user", "assistant"} and isinstance(content, str) and content.strip():
            out.append({"role": role, "content": content.strip()})
    return out


__all__ = ["generate_chat_reply", "parse_history_json"]

