import io
import json
import os
import re
from pathlib import Path
from typing import Any, Dict, Set

from dotenv import load_dotenv
from groq import Groq
from pypdf import PdfReader

_BACKEND_DIR = Path(__file__).resolve().parents[1]
load_dotenv(dotenv_path=_BACKEND_DIR / ".env", override=False)


class ResumeAnalyzer:
    def __init__(self) -> None:
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise ValueError("GROQ_API_KEY not found in environment variables")

        self.client = Groq(api_key=api_key)
        self.model = "llama-3.3-70b-versatile"

    # ============================
    # Utilities
    # ============================

    def extract_text_from_pdf(self, pdf_file: Any) -> str:
        """
        Extract text from a PDF.

        `pdf_file` can be:
        - a filesystem path (str)
        - a file-like object (supports read/seek)
        - raw PDF bytes (bytes / bytearray)
        """
        try:
            reader = PdfReader(self._normalize_pdf_input(pdf_file))
            text = "".join([page.extract_text() or "" for page in reader.pages])

            if not text.strip():
                raise ValueError(
                    "Unable to extract text from PDF. "
                    "Please upload a text-based, single-column resume."
                )

            return text.strip()
        except Exception as e:
            raise ValueError(f"PDF extraction failed: {str(e)}")

    def _normalize_pdf_input(self, pdf_file: Any) -> Any:
        if isinstance(pdf_file, (bytes, bytearray)):
            return io.BytesIO(bytes(pdf_file))
        return pdf_file

    def extract_keywords(self, text: str) -> Set[str]:
        """
        Improved keyword extraction:
        - Keeps C++, C#, .NET
        - Removes very small words
        """
        words = re.findall(r"\b[A-Za-z][A-Za-z0-9\+\#\.]{2,}\b", text)
        return set(word.lower() for word in words)

    def clamp_score(self, value: Any) -> int:
        """Ensure score is between 0–100"""
        try:
            value_int = int(value)
        except Exception:
            value_int = 0
        return max(0, min(100, value_int))

    def safe_json_parse(self, content: str) -> Dict[str, Any]:
        try:
            parsed = json.loads(content)
        except json.JSONDecodeError as exc:
            raise ValueError("Model returned invalid JSON. Try again.") from exc
        if not isinstance(parsed, dict):
            raise ValueError("Model returned unexpected JSON shape. Try again.")
        return parsed

    def calculate_weighted_score(self, breakdown: Dict[str, Any], weights: Dict[str, float]) -> int:
        total = 0.0
        for key, weight in weights.items():
            value = self.clamp_score(breakdown.get(key, 0))
            total += value * float(weight)
        return self.clamp_score(round(total))

    # ============================
    # MODE 1: Resume Only
    # ============================

    def analyze_resume_only(self, resume_text: str) -> Dict[str, Any]:
        system_prompt = """
        You are an ATS Resume Evaluator.

        Analyze the resume WITHOUT any job description using:
        - skill_coverage (0-100)
        - impact_metrics (0-100)
        - formatting (0-100)
        - clarity (0-100)

        Be strict and realistic.

        Return ONLY valid JSON:
        {
            "parameter_breakdown": {
                "skill_coverage": 0,
                "impact_metrics": 0,
                "formatting": 0,
                "clarity": 0
            },
            "strengths": [],
            "improvement_suggestions": []
        }
        """

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": resume_text},
                ],
                response_format={"type": "json_object"},
                temperature=0.2,
                max_tokens=1000,
            )

            data = self.safe_json_parse(response.choices[0].message.content)
        except Exception as e:
            raise ValueError(f"AI analysis failed: {str(e)}")

        breakdown = data.get("parameter_breakdown", {}) if isinstance(data, dict) else {}
        if not isinstance(breakdown, dict):
            breakdown = {}

        weights = {
            "skill_coverage": 0.35,
            "impact_metrics": 0.30,
            "formatting": 0.20,
            "clarity": 0.15,
        }

        overall_score = self.calculate_weighted_score(breakdown, weights)

        return {
            "mode": "resume_only",
            "score": overall_score,
            "breakdown": breakdown,
            "highlights": data.get("strengths", []) if isinstance(data, dict) else [],
            "improvements": data.get("improvement_suggestions", []) if isinstance(data, dict) else [],
        }

    # ============================
    # MODE 2: Resume vs Job Description
    # ============================

    def analyze_with_job_description(self, resume_text: str, job_description: str) -> Dict[str, Any]:
        system_prompt = """
        You are an advanced Resume–Job Description (JD) Analyzer.

        Your task is to evaluate how well a candidate's resume matches a given job description using BOTH:
        1. Keyword Matching (exact and partial matches)
        2. Semantic Understanding (meaning, context, and intent)

        IMPORTANT:
        - Do NOT rely only on exact keyword matches.
        - Understand synonyms, related concepts, and implied skills.
        - Example: "REST API development" ≈ "building backend services"
        - Example: "TensorFlow experience" ≈ "deep learning framework usage"

        Instructions:
        1. Analyze the Job Description (JD):
           - Extract required skills, preferred skills, tools, technologies, and responsibilities.
           - Group them into categories (technical skills, soft skills, domain knowledge).

        2. Analyze the Resume:
           - Extract skills, projects, experience, and achievements.
           - Identify both explicit and implicit capabilities.

        3. Perform Matching:
           - Keyword Match Score (exact matches)
           - Semantic Match Score (based on meaning and context, not exact words)
           - Give higher weight to semantic relevance than superficial keyword overlap.

        4. Scoring:
           - Provide an overall match score (0–100)
           - Breakdown: Keyword Match %, Semantic Match %

        5. Gap Analysis:
           - List missing skills (important ones from JD not found in resume)
           - Highlight partially matched skills
        
        6. Suggestions:
           - Suggest how the candidate can improve the resume for THIS JD

        7. Output Format (STRICT JSON ONLY):
        {
            "parameter_breakdown": {
                "keyword_match": 0,
                "semantic_match": 0
            },
            "matched_skills": ["Skill 1", "Skill 2"],
            "missing_skills": ["Not found 1", "Not found 2"],
            "strengths": ["Highlight 1", "Highlight 2"],
            "action_plan": ["Improvement suggestion 1"]
        }
        
        Focus on understanding meaning. Avoid giving credit for generic words. Be precise.
        """

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {
                        "role": "user",
                        "content": f"JOB DESCRIPTION:\n{job_description}\n\nRESUME:\n{resume_text}",
                    },
                ],
                response_format={"type": "json_object"},
                temperature=0.2,
                max_tokens=1200,
            )

            data = self.safe_json_parse(response.choices[0].message.content)
        except Exception as e:
            raise ValueError(f"AI matching failed: {str(e)}")

        breakdown = data.get("parameter_breakdown", {}) if isinstance(data, dict) else {}
        if not isinstance(breakdown, dict):
            breakdown = {}

        weights = {
            "keyword_match": 0.30,
            "semantic_match": 0.70
        }

        overall_score = self.calculate_weighted_score(breakdown, weights)

        # The new prompt returns missing_skills instead of us doing naive set logic
        missing_skills = data.get("missing_skills", []) if isinstance(data, dict) else []

        return {
            "mode": "resume_vs_jd",
            "score": overall_score,
            "breakdown": breakdown,
            "missing_keywords": missing_skills,
            "highlights": data.get("strengths", []) if isinstance(data, dict) else [],
            "action_plan": data.get("action_plan", []) if isinstance(data, dict) else [],
            "matched_skills": data.get("matched_skills", []) if isinstance(data, dict) else [],
        }


__all__ = ["ResumeAnalyzer"]

