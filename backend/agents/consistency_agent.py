"""
ConsistencyAgent
-----------------

This module defines the `ConsistencyAgent`, a specialist agent focused on
detecting inconsistencies within a resume.

Purpose:
- Identify mismatches or conflicts in:
  - Employment dates (overlaps or gaps).
  - Job titles vs. described responsibilities.
  - Claimed skills vs. demonstrated experience.

Inputs:
- `context`: a dictionary expected to contain:
    - `parsed_resume`: structured resume representation.

Outputs (added back into the shared context):
- `consistency_warnings`: list of human-readable warning strings.

Role in Agentic Chain:
- Runs after authenticity checks in the evaluation workflow.
- Feeds into risk prediction and roadmap generation to highlight structural
  issues in the candidate's career story.
"""

from typing import Dict, Any, List

from backend.utils.llm_client import OpenAIClient
from backend.utils import prompts


class ConsistencyAgent:
    """
    Agent that analyzes internal consistency of the resume.

    In a full implementation, this agent would:
    - Use LLM reasoning to track timelines and ensure logical progression.
    - Surface overlapping roles or unexplained gaps.
    - Cross-check titles against bullet points and claimed skills.
    Currently, it returns deterministic placeholder warnings.
    """

    def __init__(self, llm_client: OpenAIClient) -> None:
        self._llm_client = llm_client

    def run(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute consistency analysis.

        Parameters
        ----------
        context:
            Shared context dictionary containing at least `parsed_resume`.

        Returns
        -------
        Dict[str, Any]
            A dictionary with key:
            - `consistency_warnings`
        """
        parsed_resume = context.get("parsed_resume", {})

        prompt = prompts.CONSISTENCY_ANALYSIS_PROMPT.format(
            parsed_resume=parsed_resume,
        )

        # TODO: Call LLM here using structured prompt.
        # response = self._llm_client.generate_response(prompt)
        # consistency_warnings = some_parser(response)

        consistency_warnings: List[str] = [
            "Job titles suggest senior ownership, but bullet points focus mostly on individual tasks."
        ]

        return {"consistency_warnings": consistency_warnings}


__all__ = ["ConsistencyAgent"]

