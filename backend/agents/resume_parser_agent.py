"""
ResumeParserAgent
-----------------

This module defines the `ResumeParserAgent`, a specialist agent responsible for
extracting structured information from a raw resume.

Purpose:
- Convert free-form resume text into a normalized structure that other agents
  in the pipeline can easily consume.
- Identify sections (summary, experience, education, skills) and key entities
  (titles, companies, dates, tools, technologies).

Inputs:
- `context`: a dictionary that must at least contain:
    - `resume_text`: raw resume content as a string.
    - `job_description` (optional): reference role description.

Outputs (added back into the shared context):
- `parsed_resume`: high-level structured representation.
- `extracted_skills`: list of skills/keywords inferred from the resume.
- Any other lightweight metadata that downstream agents may build upon.

Role in Agentic Chain:
- This is the **first agent** in the evaluation workflow.
- Its output becomes the foundation for ATS scoring, role matching, authenticity
  checks, and all later reasoning steps.
"""

from typing import Dict, Any

from backend.utils.llm_client import OpenAIClient
from backend.utils import prompts


class ResumeParserAgent:
    """
    Agent that parses a free-form resume into structured data.

    This class encapsulates the prompt construction and (eventual) LLM call that
    will convert raw text into a machine-readable structure. For now, the LLM
    interaction is stubbed out so that the rest of the orchestration and data
    flow can be developed independently.
    """

    def __init__(self, llm_client: OpenAIClient) -> None:
        self._llm_client = llm_client

    def run(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the resume parsing step.

        Parameters
        ----------
        context:
            Shared context dictionary, containing at least `resume_text`.

        Returns
        -------
        Dict[str, Any]
            A dictionary with keys such as:
            - `parsed_resume`
            - `extracted_skills`
        """
        resume_text: str = context.get("resume_text", "")
        job_description: str = context.get("job_description", "") or ""

        # Build a structured prompt for the LLM using central templates.
        prompt = prompts.RESUME_PARSING_PROMPT.format(
            resume_text=resume_text,
            job_description=job_description,
        )

        # TODO: Call LLM here using structured prompt.
        # response = self._llm_client.generate_response(prompt)
        # parsed_output = some_json_parser(response)
        # For now, we return a simple deterministic placeholder structure so
        # that the rest of the system can be wired and tested.

        parsed_output = {
            "parsed_resume": {
                "summary": "Placeholder summary extracted from resume.",
                "experience": [],
                "education": [],
                "skills": [],
            },
            "extracted_skills": ["python", "fastapi", "react"],
        }

        return parsed_output


__all__ = ["ResumeParserAgent"]

