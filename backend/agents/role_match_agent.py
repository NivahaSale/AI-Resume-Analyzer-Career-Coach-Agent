"""
RoleMatchAgent
---------------

This module defines the `RoleMatchAgent`, a specialist agent responsible for
evaluating how well a candidate's resume aligns with a target role or job
description.

Purpose:
- Perform skill gap analysis between the candidate profile and the target role.
- Identify strengths, weaknesses, and missing competencies.

Inputs:
- `context`: a dictionary that should contain:
    - `parsed_resume`: structured resume representation.
    - `extracted_skills`: skills from the resume.
    - `job_description` (optional but recommended).

Outputs (added back into the shared context):
- `role_match_score`: numeric indicator (0–1 or 0–100) of fit.
- `skill_gaps`: list of skills that appear important for the target role but
  are missing or weak in the resume.

Role in Agentic Chain:
- Runs after ATS scoring in the evaluation workflow.
- Provides targeted information that feeds into risk prediction and roadmap
  generation, helping the system reason about how to close identified gaps.
"""

from typing import Dict, Any, List

from backend.utils.llm_client import OpenAIClient
from backend.utils import prompts


class RoleMatchAgent:
    """
    Agent that analyzes role fit and skill gaps.

    The real implementation would:
    - Parse the job description into a competency model.
    - Cross-reference that model against the parsed resume.
    - Use an LLM to judge depth and recency of experience.
    Currently, it returns deterministic placeholder values.
    """

    def __init__(self, llm_client: OpenAIClient) -> None:
        self._llm_client = llm_client

    def run(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute role matching and skill gap analysis.

        Parameters
        ----------
        context:
            Shared context with parsed resume and job description.

        Returns
        -------
        Dict[str, Any]
            A dictionary with keys:
            - `role_match_score`
            - `skill_gaps`
        """
        parsed_resume = context.get("parsed_resume", {})
        job_description = context.get("job_description", "") or ""
        extracted_skills: List[str] = context.get("extracted_skills", [])

        prompt = prompts.SKILL_DEPTH_ANALYSIS_PROMPT.format(
            parsed_resume=parsed_resume,
            job_description=job_description,
            extracted_skills=extracted_skills,
        )

        # TODO: Call LLM here using structured prompt.
        # response = self._llm_client.generate_response(prompt)
        # role_match_score, skill_gaps = some_parser(response)

        # Placeholder skill gap example to drive downstream UI / logic.
        skill_gaps = ["system design", "cloud architecture"]
        role_match_score = 0.68

        return {
            "role_match_score": role_match_score,
            "skill_gaps": skill_gaps,
        }


__all__ = ["RoleMatchAgent"]

