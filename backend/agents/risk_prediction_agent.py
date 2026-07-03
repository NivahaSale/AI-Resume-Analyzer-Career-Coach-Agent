"""
RiskPredictionAgent
--------------------

This module defines the `RiskPredictionAgent`, which synthesizes the outputs of
earlier agents into a high-level interview/hiring risk classification.

Purpose:
- Combine ATS score, role match, authenticity flags, and consistency warnings
  into a compact risk label ("low", "medium", "high").

Inputs:
- `context`: a dictionary expected to contain:
    - `ats_score`
    - `role_match_score`
    - `authenticity_flags`
    - `consistency_warnings`

Outputs (added back into the shared context):
- `risk_level`: categorical risk label.
- `risk_rationale`: short text explanation.

Role in Agentic Chain:
- Runs after consistency analysis in the evaluation workflow.
- Its classification guides the tone and priority of the roadmap.
"""

from typing import Dict, Any, List

from backend.utils.llm_client import OpenAIClient
from backend.utils import prompts


class RiskPredictionAgent:
    """
    Agent that classifies candidate risk level.

    In a full LLM-powered implementation, this agent would apply nuanced rules
    and reasoning to weigh each upstream signal. For now, it implements a
    simple, deterministic heuristic so that downstream components (e.g., UI)
    have realistic-looking data to work with.
    """

    def __init__(self, llm_client: OpenAIClient) -> None:
        self._llm_client = llm_client

    def run(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute risk prediction.

        Parameters
        ----------
        context:
            Shared context with ATS, role match, authenticity, and consistency
            information.

        Returns
        -------
        Dict[str, Any]
            A dictionary with keys:
            - `risk_level`
            - `risk_rationale`
        """
        ats_score: float = float(context.get("ats_score", 0.0))
        role_match_score: float = float(context.get("role_match_score", 0.0))
        authenticity_flags: List[str] = context.get("authenticity_flags", [])
        consistency_warnings: List[str] = context.get("consistency_warnings", [])

        prompt = prompts.RISK_CLASSIFICATION_PROMPT.format(
            ats_result={"ats_score": ats_score},
            role_match_result={"role_match_score": role_match_score},
            authenticity_result={"authenticity_flags": authenticity_flags},
            consistency_result={"consistency_warnings": consistency_warnings},
        )

        # TODO: Call LLM here using structured prompt.
        # response = self._llm_client.generate_response(prompt)
        # risk_level, rationale = some_parser(response)

        # Placeholder heuristic: combine signals to derive a risk bucket.
        penalty = 0
        penalty += len(authenticity_flags) * 0.1
        penalty += len(consistency_warnings) * 0.1

        composite_score = (ats_score / 100.0 + role_match_score) / 2.0 - penalty

        if composite_score >= 0.75:
            risk_level = "low"
        elif composite_score >= 0.5:
            risk_level = "medium"
        else:
            risk_level = "high"

        risk_rationale = (
            "Risk level is derived from ATS score, role fit, and the number of "
            "authenticity/consistency concerns. This is a heuristic placeholder."
        )

        return {
            "risk_level": risk_level,
            "risk_rationale": risk_rationale,
        }


__all__ = ["RiskPredictionAgent"]

