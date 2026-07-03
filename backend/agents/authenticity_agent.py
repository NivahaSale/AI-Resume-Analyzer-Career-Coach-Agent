"""
AuthenticityAgent
------------------

This module defines the `AuthenticityAgent`, a specialist agent that attempts
to surface potentially shallow or inflated claims in a candidate's resume.

Purpose:
- Detect patterns such as buzzword stuffing, vague responsibility statements, or
  claims of seniority that are unsupported by experience details.

Inputs:
- `context`: a dictionary expected to contain:
    - `parsed_resume`: structured resume representation from `ResumeParserAgent`.

Outputs (added back into the shared context):
- `authenticity_flags`: list of strings describing potential concerns.

Role in Agentic Chain:
- Runs after role matching in the evaluation workflow.
- Its findings are considered by the `RiskPredictionAgent` and help inform the
  final career report and roadmap.
"""

from typing import Dict, Any, List

from backend.utils.llm_client import OpenAIClient
from backend.utils import prompts


class AuthenticityAgent:
    """
    Agent that heuristically evaluates the authenticity of resume content.

    The real implementation would use nuanced LLM reasoning to:
    - Compare claimed responsibilities with depth of examples.
    - Detect overuse of generic buzzwords without specifics.
    - Identify suspicious leaps in seniority.
    For now, this agent returns deterministic placeholder flags so that the
    orchestration pipeline can be exercised end-to-end.
    """

    def __init__(self, llm_client: OpenAIClient) -> None:
        self._llm_client = llm_client

    def run(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the authenticity analysis step.

        Parameters
        ----------
        context:
            Shared context dictionary containing at least `parsed_resume`.

        Returns
        -------
        Dict[str, Any]
            A dictionary with key:
            - `authenticity_flags`
        """
        parsed_resume = context.get("parsed_resume", {})

        prompt = prompts.AUTHENTICITY_ANALYSIS_PROMPT.format(
            parsed_resume=parsed_resume,
        )

        # TODO: Call LLM here using structured prompt.
        # response = self._llm_client.generate_response(prompt)
        # authenticity_flags = some_parser(response)

        authenticity_flags: List[str] = [
            "Certain bullet points lack concrete impact metrics (e.g., percentages, revenue)."
        ]

        return {"authenticity_flags": authenticity_flags}


__all__ = ["AuthenticityAgent"]

