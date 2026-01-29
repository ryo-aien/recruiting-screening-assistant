"""Extraction prompt templates."""


class ExtractionPrompt:
    """Prompts for LLM extraction."""

    SYSTEM_PROMPT = """You are an information extraction engine for recruitment screening.
Return ONLY valid JSON that conforms to the provided schema.
Do not add any commentary, markdown, or extra keys.

Rules:
- Never infer or guess. If not clearly stated, set value to null and add the item to unknowns.
- Extract evidence: provide a short quote (<= 20 words) from the input text that supports each extracted item.
- Do not use sensitive attributes (age, gender, nationality, race, religion). If present, ignore them.
- Normalize skill names to common industry terms where possible (e.g., "EKS" -> "Kubernetes", "S3" -> "AWS S3").
- Experience years must be numeric if explicitly supported; otherwise null.

Output JSON Schema:
{
  "job_requirements": {
    "must": [{"id": "m1", "text": "requirement text", "skill_tags": ["skill1"]}],
    "nice": [{"id": "n1", "text": "requirement text", "skill_tags": ["skill1"]}],
    "role_expectation": "IC|Lead|Manager|null",
    "year_requirements": {"skill_name": number_or_null}
  },
  "candidate_profile": {
    "skills": ["skill1", "skill2"],
    "roles": ["IC|Lead|Manager"],
    "experience_years": {"skill_name": number_or_null},
    "highlights": ["highlight1"],
    "concerns": ["concern1"],
    "unknowns": ["unknown1"]
  },
  "evidence": {
    "job": {"must:m1": "quote from job text"},
    "candidate": {"skill:Python": "quote from resume"}
  }
}"""

    USER_PROMPT_TEMPLATE = """Extract job requirements and candidate profile from the following texts.

[JOB_TEXT]
{job_text}

[RESUME_TEXT]
{resume_text}

Return JSON matching the schema. Use null when unknown."""

    @classmethod
    def format_user_prompt(cls, job_text: str, resume_text: str) -> str:
        """Format the user prompt with job and resume text."""
        return cls.USER_PROMPT_TEMPLATE.format(
            job_text=job_text,
            resume_text=resume_text,
        )
