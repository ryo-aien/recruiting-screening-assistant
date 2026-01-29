"""Must requirements scorer."""

import logging
from typing import Any

logger = logging.getLogger(__name__)


class MustScorer:
    """Calculate Must score based on requirement satisfaction."""

    def calculate(
        self,
        job_requirements: dict[str, Any],
        candidate_profile: dict[str, Any],
    ) -> tuple[float, list[str]]:
        """Calculate Must score.

        Args:
            job_requirements: Extracted job requirements
            candidate_profile: Extracted candidate profile

        Returns:
            Tuple of (score 0-1, list of unsatisfied must requirement texts)
        """
        must_requirements = job_requirements.get("must", [])
        if not must_requirements:
            return 1.0, []  # No requirements = full score

        year_requirements = job_requirements.get("year_requirements", {})
        candidate_skills = set(s.lower() for s in candidate_profile.get("skills", []))
        candidate_years = {
            k.lower(): v
            for k, v in candidate_profile.get("experience_years", {}).items()
            if v is not None
        }

        satisfied_count = 0
        must_gaps = []

        for req in must_requirements:
            skill_tags = [t.lower() for t in req.get("skill_tags", [])]
            req_text = req.get("text", "")

            # Check if any skill tag is in candidate skills
            skill_match = any(tag in candidate_skills for tag in skill_tags)

            if not skill_match:
                # Check for partial matches
                skill_match = any(
                    any(tag in skill or skill in tag for skill in candidate_skills)
                    for tag in skill_tags
                )

            if skill_match:
                # Check year requirements if applicable
                year_satisfied = True
                for tag in skill_tags:
                    if tag in year_requirements and year_requirements[tag]:
                        required_years = year_requirements[tag]
                        candidate_year = candidate_years.get(tag)
                        if candidate_year is None or candidate_year < required_years:
                            year_satisfied = False
                            break

                if year_satisfied:
                    satisfied_count += 1
                else:
                    must_gaps.append(req_text)
            else:
                must_gaps.append(req_text)

        score = satisfied_count / len(must_requirements) if must_requirements else 1.0
        logger.info(
            f"Must score: {score:.2f} ({satisfied_count}/{len(must_requirements)} satisfied)"
        )
        return score, must_gaps
