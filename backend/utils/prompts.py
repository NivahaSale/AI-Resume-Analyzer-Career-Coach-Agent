"""
Central repository of prompt templates for all agents.

Rather than scattering prompt strings throughout agent implementations, this
module collects them in one place. This improves:
- Maintainability: prompts can be iterated on without touching orchestration
  or business logic.
- Consistency: shared concepts (e.g., scoring scales, tone) can be kept uniform.
- Testability: prompts can be inspected and validated independently.

Each constant below is a high-level template; the agents format these with
runtime values (resume text, job descriptions, context dictionaries, etc.).
"""

# NOTE:
# - These templates intentionally remain generic and descriptive.
# - They do NOT contain provider-specific instructions or system messages.
# - Real implementations may extend them to include JSON schemas or tool calls.


RESUME_PARSING_PROMPT = """
You are an expert technical recruiter and resume analyst.

Task:
- Parse the following resume into a structured JSON object.
- Identify sections (summary, experience, education, skills).
- Extract key entities such as job titles, companies, dates, and technologies.

Inputs:
- Resume text:
{resume_text}

- (Optional) Job description for context:
{job_description}

Output JSON keys:
- summary: short textual overview.
- experience: list of roles with title, company, dates, and bullet points.
- education: list of degrees/certifications.
- skills: list of normalized skill tokens (e.g., 'python', 'react').
"""


ATS_SCORING_PROMPT = """
You are simulating an Applicant Tracking System (ATS).

Task:
- Evaluate how well the parsed resume matches the target role description.
- Consider keyword coverage, role alignment, and basic formatting.

Parsed resume (JSON-like structure):
{parsed_resume}

Job description:
{job_description}

Output JSON keys:
- ats_score: number from 0 to 100.
- breakdown: object with sub-scores for 'keyword_match', 'formatting',
  and 'role_alignment'.
"""


SKILL_DEPTH_ANALYSIS_PROMPT = """
You are a senior hiring manager evaluating skill depth.

Task:
- Analyze the candidate's skills against the job description.
- Identify which skills are strong vs. missing or shallow.

Parsed resume:
{parsed_resume}

Job description:
{job_description}

Extracted skills:
{extracted_skills}

Output JSON keys:
- role_match_score: number from 0.0 to 1.0 indicating fit.
- skill_gaps: list of missing or weak skills that matter for the role.
"""


AUTHENTICITY_ANALYSIS_PROMPT = """
You are an experienced interviewer detecting authenticity in resumes.

Task:
- Review the parsed resume for signs of shallow or inflated claims.
- Focus on buzzword stuffing, vague responsibilities, or unlikely seniority.

Parsed resume:
{parsed_resume}

Output JSON keys:
- authenticity_flags: list of strings describing potential concerns.
"""


CONSISTENCY_ANALYSIS_PROMPT = """
You are a detail-oriented recruiter checking resume consistency.

Task:
- Look for inconsistencies across roles, dates, titles, and claimed skills.
- Flag overlapping dates, contradictory titles, or mismatched seniority.

Parsed resume:
{parsed_resume}

Output JSON keys:
- consistency_warnings: list of strings describing any inconsistencies.
"""


RISK_CLASSIFICATION_PROMPT = """
You are a hiring manager classifying interview risk.

Task:
- Based on ATS score, role match, authenticity flags, and consistency warnings,
  classify the hiring/interview risk as 'low', 'medium', or 'high'.
- Explain briefly why.

Context:
- ATS result:
{ats_result}

- Role match result:
{role_match_result}

- Authenticity result:
{authenticity_result}

- Consistency result:
{consistency_result}

Output JSON keys:
- risk_level: one of 'low', 'medium', 'high'.
- rationale: short explanation string.
"""


ROADMAP_GENERATION_PROMPT = """
You are a career and resume coach.

Task:
- Generate a concrete roadmap to improve this candidate's profile.
- Roadmap should include skills to build, projects to complete, and approximate
  timelines for each.

Context:
- Parsed resume:
{parsed_resume}

- Skill gaps:
{skill_gaps}

- Risk level:
{risk_level}

Output JSON keys:
- overview: narrative description of the strategy.
- entries: list of objects with keys 'skill', 'project', 'timeline'.
"""


MENTORING_PROMPT = """
You are a personalized career mentor.

Task:
- Based on the candidate's resume (if provided), target role, experience level,
  and learning preferences, outline a mentoring plan.

Inputs:
- Resume (optional):
{resume_text}

- Target role:
{target_role}

- Experience level:
{experience_level}

- Learning preferences:
{learning_preferences}

Output JSON keys:
- mentoring_focus: textual description of key focus areas.
- suggested_themes: list of topics or themes for mentoring sessions.
"""


RECRUITER_SIMULATION_PROMPT = """
You are simulating an interview from the perspective of a {mode} recruiter.

Modes:
- hr: focus on behavioral signals, cultural fit, and basic screening.
- technical: focus on technical depth, architecture, and problem solving.
- manager: focus on ownership, collaboration, and business impact.

Inputs:
- Resume text:
{resume_text}

- Job description (optional):
{job_description}

- Interview context (optional):
{interview_context}

Output JSON keys:
- perspective_summary: paragraph summarizing how this recruiter persona
  perceives the candidate.
- suggested_questions: list of interview questions to ask.
- feedback: concise recommendations for improving performance in this type of
  interview.
"""


__all__ = [
    "RESUME_PARSING_PROMPT",
    "ATS_SCORING_PROMPT",
    "SKILL_DEPTH_ANALYSIS_PROMPT",
    "AUTHENTICITY_ANALYSIS_PROMPT",
    "CONSISTENCY_ANALYSIS_PROMPT",
    "RISK_CLASSIFICATION_PROMPT",
    "ROADMAP_GENERATION_PROMPT",
    "MENTORING_PROMPT",
    "RECRUITER_SIMULATION_PROMPT",
]

