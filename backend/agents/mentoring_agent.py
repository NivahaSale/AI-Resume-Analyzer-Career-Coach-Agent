"""
MentoringAgent
---------------

This module defines the `MentoringAgent`, a specialist agent that interprets
the candidate's mentoring and learning context.

Purpose:
- Read the candidate's goals, experience level, and learning preferences.
- Distill them into a focused mentoring strategy that a downstream roadmap
  generator can translate into concrete steps.

Inputs:
- `context`: a dictionary that may contain:
    - `resume_text` (optional)
    - `target_role`
    - `experience_level`
    - `learning_preferences`

Outputs (added back into the shared context):
- `mentoring_focus`: narrative of key focus areas for mentoring.
- `suggested_themes`: list of topic themes (e.g., "system design", "leadership").

Role in Agentic Chain:
- First step in the mentoring workflow.
- Provides high-level mentoring direction for the `RoadmapAgent`.
"""

from typing import Dict, Any, List

from backend.utils.llm_client import OpenAIClient
from backend.utils import prompts


class MentoringAgent:
    """
    Agent that translates user context into mentoring focus areas.

    The full implementation would call an LLM to:
    - Interpret the candidate's resume, aspirations, and self-assessed level.
    - Suggest focus areas and recurring themes for mentoring sessions.
    For now, the logic is stubbed and returns deterministic placeholder values.
    """

    def __init__(self, llm_client: OpenAIClient) -> None:
        self._llm_client = llm_client

    def run(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the mentoring analysis step.

        Parameters
        ----------
        context:
            Shared context dictionary containing mentoring-related inputs.

        Returns
        -------
        Dict[str, Any]
            A dictionary with keys:
            - `mentoring_focus`
            - `suggested_themes`
        """
        resume_text: str = context.get("resume_text", "") or ""
        target_role: str = context.get("target_role", "") or ""
        experience_level: str = context.get("experience_level", "") or ""
        learning_preferences: str = context.get("learning_preferences", "") or ""

        prompt = prompts.MENTORING_PROMPT.format(
            resume_text=resume_text,
            target_role=target_role,
            experience_level=experience_level,
            learning_preferences=learning_preferences,
        )

        # TODO: Call LLM here using structured prompt.
        # response = self._llm_client.generate_response(prompt)
        # mentoring_focus, suggested_themes = some_parser(response)

        themes: List[str] = [
            "senior-level system design",
            "ownership and impact communication",
            "career narrative and storytelling",
        ]
        mentoring_focus = (
            "Strengthen core system design and communication skills to prepare for "
            "senior-level interviews and cross-functional collaboration."
        )

        return {
            "mentoring_focus": mentoring_focus,
            "suggested_themes": themes,
        }


__all__ = ["MentoringAgent"]

