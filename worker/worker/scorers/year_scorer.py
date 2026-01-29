"""Year/experience requirements scorer."""

import logging
from typing import Any

logger = logging.getLogger(__name__)


class YearScorer:
    """Calculate Year score based on experience years."""

    def calculate(
        self,
        job_requirements: dict[str, Any],
        candidate_profile: dict[str, Any],
    ) -> float:
        """Calculate Year score.

        Uses linear clipping: score = clip(actual / required, 0, 1)
        Final score is average across all required skills.

        Args:
            job_requirements: Extracted job requirements
            candidate_profile: Extracted candidate profile

        Returns:
            Score between 0 and 1
        """
        year_requirements = job_requirements.get("year_requirements", {})
        if not year_requirements:
            return 1.0  # No requirements = full score

        candidate_years = candidate_profile.get("experience_years", {})

        # Normalize keys to lowercase for matching
        candidate_years_lower = {
            k.lower(): v for k, v in candidate_years.items() if v is not None
        }

        scores = []
        for skill, required_years in year_requirements.items():
            if required_years is None or required_years <= 0:
                continue

            skill_lower = skill.lower()
            actual_years = candidate_years_lower.get(skill_lower)

            if actual_years is None:
                # No data = conservative 0
                scores.append(0.0)
            else:
                # Linear clip
                score = min(actual_years / required_years, 1.0)
                scores.append(max(score, 0.0))

        if not scores:
            return 1.0  # No valid requirements

        final_score = sum(scores) / len(scores)
        logger.info(f"Year score: {final_score:.2f} (from {len(scores)} requirements)")
        return final_score
