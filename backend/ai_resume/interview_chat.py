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


def _get_system_prompt(mode: str) -> str:
    normalized_mode = (mode or "hr").lower().strip()
    return f"""
You are an expert {normalized_mode.upper()} Interviewer conducting a mock interview with a candidate.

You will be provided with:
1. The candidate's Resume
2. The Target Job Description (if applicable)
3. The ongoing chat history of the interview.

Your goal is to simulate a realistic, challenging, but professional interview loop.
- Ask ONLY ONE question at a time. Do not overwhelm the candidate.
- If the candidate answers, provide brief feedback on their response, and then either ask a follow-up or move to the next topic.
- If this is the start of the interview, introduce yourself briefly as the {normalized_mode.upper()} interviewer and ask the very first opening question.
- Stay strictly in character! Do not drop the persona to act as a general AI assistant.

Return ONLY valid JSON in this exact shape:
{{
  "reply": "Your conversational response to the candidate, acting as the interviewer."
}}
"""


def generate_interview_reply(
    *,
    mode: str,
    user_message: str | None,
    history: List[ChatMessage],
    resume_text: str | None,
    job_description: str | None,
) -> Dict[str, Any]:
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise ValueError("GROQ_API_KEY not found in environment variables")
        
    client = Groq(api_key=api_key)
    model = "llama-3.3-70b-versatile"

    system_prompt = _get_system_prompt(mode)

    context_block = f"JOB_DESCRIPTION (optional):\n{job_description or ''}\n\nRESUME (optional):\n{resume_text or ''}".strip()

    messages: List[Dict[str, str]] = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": "Context details below:\n" + context_block},
    ]

    for msg in history[-15:]:
        role = (msg.get("role") or "").strip()
        content = (msg.get("content") or "").strip()
        if role in {"user", "assistant"} and content:
            messages.append({"role": role, "content": content})

    if user_message and user_message.strip():
        messages.append({"role": "user", "content": user_message.strip()})
    elif not history:
        messages.append({"role": "user", "content": "Please start the mock interview. Introduce yourself and ask the first question."})

    response = client.chat.completions.create(
        model=model,
        messages=messages,
        response_format={"type": "json_object"},
        temperature=0.5,
        max_tokens=800,
    )

    data = _safe_json_object(response.choices[0].message.content or "{}")
    reply = data.get("reply", "")
    if not isinstance(reply, str):
        reply = "I'm sorry, I'm having trouble processing that right now."

    return {
        "reply": reply.strip()
    }

__all__ = ["generate_interview_reply", "ChatMessage"]
