"""
RoadmapAgent
-------------

This module defines the `RoadmapAgent`, which is responsible for turning
upstream analysis into a concrete, actionable roadmap.

Purpose:
- Translate skill gaps, risk level, and mentoring signals into:
  - Skills to focus on.
  - Projects to execute.
  - Approximate timelines.

Inputs:
- `context`: a dictionary that may contain:
    - `parsed_resume`
    - `skill_gaps`
    - `risk_level`
    - `mentoring_focus` (from `MentoringAgent` for mentoring workflows)

Outputs (returned from `run` and often stored in context as `roadmap`):
- `overview`: high-level narrative of the plan.
- `entries`: list of roadmap entries with `skill`, `project`, `timeline`.

Role in Agentic Chain:
- Final step in both evaluation and mentoring workflows.
- Synthesizes multiple signals into a unified improvement plan.
"""

from typing import Dict, Any, List

from backend.utils.llm_client import OpenAIClient
from backend.utils import prompts


class RoadmapAgent:
    """
    Agent that generates a structured improvement roadmap.

    The real implementation would lean heavily on an LLM to reason about:
    - Candidate strengths and gaps.
    - Realistic project scopes and timelines.
    - Progressive skill building paths.
    For now, it returns a deterministic placeholder roadmap.
    """

    def __init__(self, llm_client: OpenAIClient) -> None:
        self._llm_client = llm_client

    def run(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute roadmap generation.

        Parameters
        ----------
        context:
            Shared context with resume analysis outputs and optional mentoring
            insights.

        Returns
        -------
        Dict[str, Any]
            A dictionary with keys:
            - `overview`
            - `entries`
        """
        parsed_resume = context.get("parsed_resume", {})
        skill_gaps: List[str] = context.get("skill_gaps", [])
        risk_level: str = context.get("risk_level", "unknown")
        mentoring_focus: str = context.get("mentoring_focus", "")

        prompt = prompts.ROADMAP_GENERATION_PROMPT.format(
            parsed_resume=parsed_resume,
            skill_gaps=skill_gaps,
            risk_level=risk_level,
        )

        # TODO: Call LLM here using structured prompt.
        # response = self._llm_client.generate_response(prompt)
        # roadmap = some_parser(response)

        # Placeholder deterministic roadmap.
        overview_parts = [
            "Focus on solidifying core backend and system design skills.",
            "Gradually expand into cloud-native patterns and leadership behaviors.",
        ]
        if mentoring_focus:
            overview_parts.append(f"Special attention to: {mentoring_focus}")

        overview = " ".join(overview_parts)

        entries = [
            {
                "skill": "system design",
                "project": "Design and document a scalable microservice architecture.",
                "timeline": "2-4 weeks",
            },
            {
                "skill": "cloud architecture",
                "project": "Deploy a containerized FastAPI service on a cloud provider.",
                "timeline": "3-5 weeks",
            },
            {
                "skill": "communication",
                "project": "Lead a technical brownbag session on a past project.",
                "timeline": "1-2 weeks",
            },
        ]

        return {"overview": overview, "entries": entries}


__all__ = ["RoadmapAgent"]

