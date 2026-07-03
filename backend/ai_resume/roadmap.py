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


def generate_roadmap(
    *,
    resume_text: str,
    job_description: str | None,
    ats_mode: str,
    missing_keywords: List[str] | None,
) -> Dict[str, Any]:
    """
    Generate a RoadmapResponse-like payload:
      { "overview": str, "entries": [{ "skill": str, "project": str, "timeline": str }, ...] }
    """
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise ValueError("GROQ_API_KEY not found in environment variables")

    client = Groq(api_key=api_key)
    model = "llama-3.3-70b-versatile"

    missing_keywords = missing_keywords or []
    keywords_context = ", ".join(missing_keywords[:20]) if missing_keywords else ""

    system_prompt = """
You are a career coach and resume improvement planner.

Create an actionable improvement roadmap based on the candidate's actual resume content
(and optionally a job description).

Return ONLY valid JSON with this exact shape:
{
  "overview": "string",
  "entries": [
    { "skill": "string", "project": "string", "timeline": "string" }
  ]
}

Hard requirements:
- The plan MUST be specific to the resume. Reference at least 3 concrete details found in the resume
  (e.g., tools, projects, domains, achievements). If the resume is thin, reference what is present.
- DO NOT reuse generic templates. Avoid generic items like "system design" / "cloud architecture" /
  "communication" unless they are clearly justified by the resume/job description.
- overview: 2-4 sentences, pragmatic and encouraging.
- entries: 5 to 8 items.
- timelines must be realistic (e.g., "3-5 days", "1-2 weeks", "3-4 weeks").
- projects must be concrete deliverables (portfolio-ready), scoped to the candidate level.
- If a job description is provided, prioritize missing keywords/skills, but do NOT just list keywords.
"""

    user_prompt = f"""
ATS_MODE: {ats_mode}

MISSING_KEYWORDS (if any): {keywords_context}

JOB_DESCRIPTION (optional):
{job_description or ""}

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
        temperature=0.3,
        max_tokens=1200,
    )

    data = _safe_json_object(response.choices[0].message.content)

    # Light validation/normalization to keep the API stable.
    overview = data.get("overview", "")
    if not isinstance(overview, str):
        overview = ""

    entries_raw = data.get("entries", [])
    entries: List[Dict[str, str]] = []
    if isinstance(entries_raw, list):
        for item in entries_raw:
            if not isinstance(item, dict):
                continue
            skill = item.get("skill", "")
            project = item.get("project", "")
            timeline = item.get("timeline", "")
            if all(isinstance(x, str) for x in (skill, project, timeline)) and (skill or project or timeline):
                entries.append({"skill": skill.strip(), "project": project.strip(), "timeline": timeline.strip()})

    return {"overview": overview.strip(), "entries": entries}


def generate_mentoring_roadmap(
    *,
    resume_text: str | None,
    target_role: str | None,
    experience_level: str | None,
    learning_preferences: str | None,
) -> Dict[str, Any]:
    """
    Generate a learning-focused roadmap (mentoring mode).

    Returns a RoadmapResponse-like payload:
      { "overview": str, "entries": [{ "skill": str, "project": str, "timeline": str }, ...] }
    """
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise ValueError("GROQ_API_KEY not found in environment variables")

    client = Groq(api_key=api_key)
    model = "llama-3.3-70b-versatile"

    system_prompt = """
You are a senior mentor designing a practical learning roadmap for a candidate.

Return ONLY valid JSON with this exact shape:
{
  "overview": "string",
  "entries": [
    { "skill": "string", "project": "string", "timeline": "string" }
  ]
}

Guidelines:
- Use the user's target role, experience level, and learning preferences.
- If a resume is provided, tailor the roadmap to their current strengths/weaknesses.
- Prefer hands-on projects. Each project must be a concrete deliverable.
- Include a mix of: fundamentals, projects, interview prep, and portfolio improvements.
- entries: 6 to 10 items with realistic timelines.
- Avoid generic filler; be specific to the role (e.g., ML Engineer vs Backend).
"""

    user_prompt = f"""
TARGET_ROLE: {target_role or ""}
EXPERIENCE_LEVEL: {experience_level or ""}
LEARNING_PREFERENCES: {learning_preferences or ""}

RESUME (optional, may be empty):
{resume_text or ""}
""".strip()

    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        response_format={"type": "json_object"},
        temperature=0.4,
        max_tokens=1400,
    )

    data = _safe_json_object(response.choices[0].message.content)

    overview = data.get("overview", "")
    if not isinstance(overview, str):
        overview = ""

    entries_raw = data.get("entries", [])
    entries: List[Dict[str, str]] = []
    if isinstance(entries_raw, list):
        for item in entries_raw:
            if not isinstance(item, dict):
                continue
            skill = item.get("skill", "")
            project = item.get("project", "")
            timeline = item.get("timeline", "")
            if all(isinstance(x, str) for x in (skill, project, timeline)) and (skill or project or timeline):
                entries.append({"skill": skill.strip(), "project": project.strip(), "timeline": timeline.strip()})

    return {"overview": overview.strip(), "entries": entries}


__all__ = ["generate_roadmap", "generate_mentoring_roadmap"]

