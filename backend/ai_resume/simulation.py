from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any, Dict, List

from dotenv import load_dotenv
from groq import Groq

_BACKEND_DIR = Path(__file__).resolve().parents[1]
load_dotenv(dotenv_path=_BACKEND_DIR / ".env", override=False)


def _safe_json_object(content: str) -> Dict[str, Any]:
    try:
        parsed = json.loads(content)
    except json.JSONDecodeError as exc:
        raise ValueError("Model returned invalid JSON.") from exc
    if not isinstance(parsed, dict):
        raise ValueError("Model returned unexpected JSON shape.")
    return parsed


def generate_simulation(
    *,
    mode: str,
    resume_text: str,
    job_description: str | None,
    interview_context: str | None,
) -> Dict[str, Any]:
    """
    Generate a SimulationResponse-like payload:
      { "perspective_summary": str, "suggested_questions": [str], "feedback": str }
    """
    normalized_mode = (mode or "").lower().strip()
    if normalized_mode not in {"hr", "technical", "manager"}:
        raise ValueError("Unsupported simulation mode. Valid modes: hr, technical, manager.")

    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise ValueError("GROQ_API_KEY not found in environment variables")

    client = Groq(api_key=api_key)
    model = "llama-3.3-70b-versatile"

    system_prompt = f"""
You are simulating a recruiter interview from the perspective of: {normalized_mode.upper()}.

Use the provided resume (and optional job description and interview context) to produce:
- a specific perspective summary
- realistic questions this recruiter would ask *based on the resume*
- actionable feedback to improve interview readiness and resume positioning

Return ONLY valid JSON with this exact shape:
{{
  "perspective_summary": "string",
  "suggested_questions": ["string"],
  "feedback": "string"
}}

Hard requirements:
- Must reference at least 2 concrete details from the resume (projects, tools, roles, education, etc.).
- Questions must be tailored; avoid generic questions unless justified by the resume/context.
- suggested_questions: 5 to 8 items.
"""

    user_prompt = f"""
JOB_DESCRIPTION (optional):
{job_description or ""}

INTERVIEW_CONTEXT (optional):
{interview_context or ""}

RESUME:
{resume_text}
""".strip()

    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        response_format={"type": "json_object"},
        temperature=0.4,
        max_tokens=1200,
    )

    data = _safe_json_object(response.choices[0].message.content)

    perspective_summary = data.get("perspective_summary", "")
    feedback = data.get("feedback", "")
    questions_raw = data.get("suggested_questions", [])

    if not isinstance(perspective_summary, str):
        perspective_summary = ""
    if not isinstance(feedback, str):
        feedback = ""

    suggested_questions: List[str] = []
    if isinstance(questions_raw, list):
        for q in questions_raw:
            if isinstance(q, str) and q.strip():
                suggested_questions.append(q.strip())

    return {
        "perspective_summary": perspective_summary.strip(),
        "suggested_questions": suggested_questions,
        "feedback": feedback.strip(),
    }


__all__ = ["generate_simulation"]

