import os
import json
import re
from groq import Groq
from dotenv import load_dotenv
from pypdf import PdfReader

load_dotenv()


class ResumeAnalyzer:
    def __init__(self):
        self.client = Groq(api_key=os.getenv("GROQ_API_KEY"))
        self.model = "llama-3.3-70b-versatile"

    # Utilities 

   # def extract_text_from_pdf(self, pdf_file):
    #    reader = PdfReader(pdf_file)
     #   return "".join([page.extract_text() or "" for page in reader.pages])
    
    def extract_text_from_pdf(self, pdf_file):
        reader = PdfReader(pdf_file)
        text = "".join([page.extract_text() or "" for page in reader.pages])
        if not text.strip():
            raise ValueError(
                "Unable to extract text from PDF. "
                "Please upload a text-based, single-column resume."
            )
        return text


    def extract_keywords(self, text):
        return set(re.findall(r'\b[A-Za-z][A-Za-z\+\#\.]{2,}\b', text))

    def calculate_weighted_score(self, breakdown, weights):
        return round(sum(breakdown[k] * weights[k] for k in weights))

    # MODE 1: Resume-only ATS

    def analyze_resume_only(self, resume_text):
        system_prompt = """
        You are an ATS Resume Evaluator.

        Analyze the resume WITHOUT any job description using:
        - skill_coverage (0-100)
        - impact_metrics (0-100)
        - formatting (0-100)
        - clarity (0-100)

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

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": resume_text}
            ],
            response_format={"type": "json_object"},
            temperature=0.1
        )

        data = json.loads(response.choices[0].message.content)

        breakdown = data["parameter_breakdown"]
        weights = {
            "skill_coverage": 0.35,
            "impact_metrics": 0.30,
            "formatting": 0.20,
            "clarity": 0.15
        }

        overall_score = self.calculate_weighted_score(breakdown, weights)

        return {
            "mode": "resume_only",
            "overall_ats_score": overall_score,
            "parameter_breakdown": breakdown,
            "strengths": data.get("strengths", []),
            "improvement_suggestions": data.get("improvement_suggestions", [])
        }

    #  MODE 2: Resume vs Job Description 

    def analyze_with_job_description(self, resume_text, job_description):
        system_prompt = """
        You are an ATS Matching Engine.

        Compare RESUME vs JOB DESCRIPTION using:
        - keyword_match (0-100)
        - experience_relevance (0-100)
        - impact_metrics (0-100)
        - formatting (0-100)

        Return ONLY valid JSON:
        {
            "parameter_breakdown": {
                "keyword_match": 0,
                "experience_relevance": 0,
                "impact_metrics": 0,
                "formatting": 0
            },
            "strengths": [],
            "action_plan": []
        }
        """

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {
                    "role": "user",
                    "content": f"JOB DESCRIPTION:\n{job_description}\n\nRESUME:\n{resume_text}"
                }
            ],
            response_format={"type": "json_object"},
            temperature=0.1
        )

        data = json.loads(response.choices[0].message.content)
        breakdown = data["parameter_breakdown"]

        weights = {
            "keyword_match": 0.40,
            "experience_relevance": 0.30,
            "impact_metrics": 0.20,
            "formatting": 0.10
        }

        overall_score = self.calculate_weighted_score(breakdown, weights)

        # Keyword gap detection
        jd_keywords = self.extract_keywords(job_description.lower())
        resume_keywords = self.extract_keywords(resume_text.lower())
        missing_keywords = sorted(jd_keywords - resume_keywords)

        return {
            "mode": "resume_vs_jd",
            "overall_ats_score": overall_score,
            "parameter_breakdown": breakdown,
            "missing_keywords": missing_keywords[:20],
            "strengths": data.get("strengths", []),
            "action_plan": data.get("action_plan", [])
        }
