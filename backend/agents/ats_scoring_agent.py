"""
ATSScoringAgent
----------------

This module defines the `ATSScoringAgent`, a specialist agent that simulates
how an Applicant Tracking System (ATS) might evaluate a resume.

Purpose:
- Produce a synthetic ATS-style score for the resume.
- Highlight keyword density, alignment with job description, and formatting
  aspects that might influence automated screening systems.

Inputs:
- `context`: a dictionary that should contain:
    - `parsed_resume`: structured representation from `ResumeParserAgent`.
    - `extracted_skills`: list of skills identified in the resume.
    - `job_description` (optional): text of the target role description.

Outputs (added back into the shared context):
- `ats_score`: numeric score (0–100) representing ATS friendliness.
- `ats_breakdown`: lightweight explanation of how the score was derived.

Role in Agentic Chain:
- Runs **after** `ResumeParserAgent` in the evaluation workflow.
- Feeds quantitative scoring information into later agents such as
  role matching, risk prediction, and roadmap generation.
"""

from typing import Dict, Any

from backend.utils.llm_client import OpenAIClient
from backend.utils import prompts


class ATSScoringAgent:
    """
    Agent that estimates ATS compatibility of a resume.

    The real implementation would use a combination of heuristic scoring and
    LLM-based reasoning. For now, we provide a placeholder to enable the
    orchestration logic without integrating an actual LLM.
    """

    def __init__(self, llm_client: OpenAIClient) -> None:
        self._llm_client = llm_client

    def run(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the ATS scoring step.

        Parameters
        ----------
        context:
            Shared context containing parsed resume details and optional job
            description.

        Returns
        -------
        Dict[str, Any]
            A dictionary with keys:
            - `ats_score`
            - `ats_breakdown`
        """
        parsed_resume = context.get("parsed_resume", {})
        job_description = context.get("job_description", "") or ""

        prompt = prompts.ATS_SCORING_PROMPT.format(
            parsed_resume=parsed_resume,
            job_description=job_description,
        )

        # TODO: Call LLM here using structured prompt.
        # response = self._llm_client.generate_response(prompt)
        # ats_score, breakdown = some_parser(response)

        # Placeholder weighted scoring logic. In a real system, this would be
        # replaced by a more principled model-driven or data-driven approach.
        ats_score = 75.0
        breakdown = {
            "keyword_match": 0.8,
            "formatting": 0.7,
            "role_alignment": 0.75,
        }

        return {
            "ats_score": ats_score,
            "ats_breakdown": breakdown,
        }


__all__ = ["ATSScoringAgent"]

