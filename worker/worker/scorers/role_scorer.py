"""Role expectation scorer."""

import logging
from typing import Any

logger = logging.getLogger(__name__)


# Default role distance matrix
DEFAULT_ROLE_DISTANCE = {
    "IC": {"IC": 1.0, "Lead": 0.7, "Manager": 0.3},
    "Lead": {"IC": 0.7, "Lead": 1.0, "Manager": 0.7},
    "Manager": {"IC": 0.3, "Lead": 0.7, "Manager": 1.0},
}


class RoleScorer:
    """Calculate Role score based on role expectation matching."""

    def __init__(self, role_distance: dict[str, dict[str, float]] | None = None):
        self.role_distance = role_distance or DEFAULT_ROLE_DISTANCE

    def calculate(
        self,
        job_requirements: dict[str, Any],
        candidate_profile: dict[str, Any],
    ) -> float:
        """Calculate Role score.

        Args:
            job_requirements: Extracted job requirements
            candidate_profile: Extracted candidate profile

        Returns:
            Score between 0 and 1
        """
        expected_role = job_requirements.get("role_expectation")
        candidate_roles = candidate_profile.get("roles", [])

        if not expected_role:
            return 1.0  # No expectation = full score

        if not candidate_roles:
            return 0.5  # Unknown = neutral

        # Normalize role names
        expected_role = self._normalize_role(expected_role)
        normalized_roles = [self._normalize_role(r) for r in candidate_roles]

        # Get best matching score
        best_score = 0.0
        for role in normalized_roles:
            if expected_role in self.role_distance and role in self.role_distance[expected_role]:
                score = self.role_distance[expected_role][role]
                best_score = max(best_score, score)
            elif role == expected_role:
                best_score = 1.0

        # If no match found in distance matrix, use partial matching
        if best_score == 0.0:
            if any(role.lower() == expected_role.lower() for role in candidate_roles):
                best_score = 1.0
            else:
                best_score = 0.5  # Unknown matching

        logger.info(
            f"Role score: {best_score:.2f} "
            f"(expected: {expected_role}, candidate: {candidate_roles})"
        )
        return best_score

    def _normalize_role(self, role: str) -> str:
        """Normalize role name to standard form."""
        role_lower = role.lower().strip()

        # Map common variations
        if role_lower in ["ic", "individual contributor", "engineer", "developer"]:
            return "IC"
        elif role_lower in ["lead", "tech lead", "team lead", "senior"]:
            return "Lead"
        elif role_lower in ["manager", "engineering manager", "em", "director"]:
            return "Manager"

        return role
