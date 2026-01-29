"""Explanation generation prompt templates."""

import json
from typing import Any


class ExplanationPrompt:
    """Prompts for explanation generation."""

    SYSTEM_PROMPT = """You are generating an explanation for a recruitment screening score.
Use only the provided inputs and evidence. Do not invent facts.
Keep it concise and actionable for a recruiter.

Output format must be JSON with keys:
- summary (string): A 1-2 sentence summary of the candidate's fit
- strengths (array of strings, up to 3): Key strengths matching job requirements
- concerns (array of strings, up to 3): Potential concerns or gaps
- unknowns (array of strings, up to 5): Information that couldn't be verified
- must_gaps (array of strings): Must requirements that are not satisfied"""

    USER_PROMPT_TEMPLATE = """Given:
- job_requirements: {job_requirements_json}
- candidate_profile: {candidate_profile_json}
- scores: {scores_json}
- evidence: {evidence_json}

Generate the explanation JSON."""

    @classmethod
    def format_user_prompt(
        cls,
        job_requirements: dict[str, Any],
        candidate_profile: dict[str, Any],
        scores: dict[str, Any],
        evidence: dict[str, Any],
    ) -> str:
        """Format the user prompt with all required data."""
        return cls.USER_PROMPT_TEMPLATE.format(
            job_requirements_json=json.dumps(job_requirements, ensure_ascii=False),
            candidate_profile_json=json.dumps(candidate_profile, ensure_ascii=False),
            scores_json=json.dumps(scores, ensure_ascii=False),
            evidence_json=json.dumps(evidence, ensure_ascii=False),
        )
