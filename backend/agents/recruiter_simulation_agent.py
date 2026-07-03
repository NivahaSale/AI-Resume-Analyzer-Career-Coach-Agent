"""
RecruiterSimulationAgent
-------------------------

This module defines the `RecruiterSimulationAgent`, which emulates different
recruiter personas to help candidates practice for interviews.

Supported modes:
- 'hr'        → HR screening and behavioral focus.
- 'technical' → Technical depth and architecture focus.
- 'manager'   → Team fit, ownership, and business impact focus.

Purpose:
- Provide a perspective-specific summary of how the resume might be perceived.
- Suggest realistic questions the recruiter might ask.
- Offer feedback on how to better resonate with that recruiter type.

Inputs:
- `context`: a dictionary that should contain:
    - `mode`: one of 'hr', 'technical', 'manager'.
    - `resume_text`: raw resume content.
    - `job_description` (optional).
    - `interview_context` (optional).

Outputs:
- Dictionary with keys:
    - `perspective_summary`
    - `suggested_questions`
    - `feedback`

Role in Agentic Chain:
- Main (and only) agent used in the simulation workflow.
"""

from typing import Dict, Any, List

from backend.utils.llm_client import OpenAIClient
from backend.utils import prompts


class RecruiterSimulationAgent:
    """
    Agent that simulates an interview from a recruiter perspective.

    In a real implementation, this agent could:
    - Run multi-turn conversations with the candidate.
    - Adapt questioning strategy based on candidate responses.
    - Persist session state to provide longitudinal training.
    For now, it returns deterministic, mode-specific placeholder content.
    """

    def __init__(self, llm_client: OpenAIClient) -> None:
        self._llm_client = llm_client

    def run(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a single-step recruiter simulation.

        Parameters
        ----------
        context:
            Shared context containing `mode`, `resume_text`, and optional
            `job_description` and `interview_context`.

        Returns
        -------
        Dict[str, Any]
            A dictionary with mode-specific summary, questions, and feedback.
        """
        mode: str = context.get("mode", "hr")
        resume_text: str = context.get("resume_text", "") or ""
        job_description: str = context.get("job_description", "") or ""
        interview_context: str = context.get("interview_context", "") or ""

        prompt = prompts.RECRUITER_SIMULATION_PROMPT.format(
            mode=mode,
            resume_text=resume_text,
            job_description=job_description,
            interview_context=interview_context,
        )

        # TODO: Call LLM here using structured prompt.
        # response = self._llm_client.generate_response(prompt)
        # perspective_summary, suggested_questions, feedback = some_parser(response)

        # Deterministic, mode-specific placeholder behavior to make the API
        # feel realistic and easy to test from the frontend.
        if mode == "hr":
            summary = (
                "From an HR perspective, the resume suggests solid experience but could "
                "benefit from clearer outcomes and more concise formatting."
            )
            questions: List[str] = [
                "Can you describe a time you resolved a conflict within a team?",
                "What motivates you in your day-to-day work?",
                "Why are you interested in this particular role and company?",
            ]
            feedback = (
                "Clarify your career narrative and highlight 2–3 key achievements with "
                "impact metrics near the top of the resume."
            )
        elif mode == "technical":
            summary = (
                "From a technical perspective, the resume lists relevant technologies, "
                "but the depth of system design experience is not fully evident."
            )
            questions = [
                "Walk me through the architecture of a recent system you designed or worked on.",
                "How do you approach performance bottlenecks in distributed systems?",
                "Describe a challenging production incident and how you resolved it.",
            ]
            feedback = (
                "Add more detail on architecture decisions, trade-offs, and production "
                "issues you have owned or resolved."
            )
        else:  # manager
            summary = (
                "From a hiring manager perspective, the resume indicates growing ownership, "
                "but leadership impact and cross-functional collaboration examples could "
                "be highlighted more strongly."
            )
            questions = [
                "Tell me about a project where you had to influence stakeholders without direct authority.",
                "How do you prioritize work for yourself and your team under tight deadlines?",
                "Describe a time you mentored a junior engineer or peer.",
            ]
            feedback = (
                "Emphasize outcomes, leadership moments, and how your work supported "
                "broader business goals."
            )

        return {
            "perspective_summary": summary,
            "suggested_questions": questions,
            "feedback": feedback,
        }


__all__ = ["RecruiterSimulationAgent"]

