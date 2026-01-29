"""Total fit score calculator."""

import logging
from typing import Any

logger = logging.getLogger(__name__)


class TotalFitCalculator:
    """Calculate total fit score from sub-scores."""

    def __init__(
        self,
        weights: dict[str, float] | None = None,
        must_cap_enabled: bool = True,
        must_cap_value: float = 20.0,
    ):
        self.weights = weights or {
            "must": 0.45,
            "nice": 0.20,
            "year": 0.20,
            "role": 0.15,
        }
        self.must_cap_enabled = must_cap_enabled
        self.must_cap_value = must_cap_value

    def calculate(
        self,
        must_score: float,
        nice_score: float,
        year_score: float,
        role_score: float,
        has_must_gaps: bool = False,
    ) -> int:
        """Calculate total fit score.

        Args:
            must_score: Must requirements score (0-1)
            nice_score: Nice requirements score (0-1)
            year_score: Year experience score (0-1)
            role_score: Role matching score (0-1)
            has_must_gaps: Whether there are unsatisfied must requirements

        Returns:
            Total fit score (0-100)
        """
        # Calculate weighted sum
        total_fit_01 = (
            self.weights["must"] * must_score
            + self.weights["nice"] * nice_score
            + self.weights["year"] * year_score
            + self.weights["role"] * role_score
        )

        # Convert to 0-100
        total_fit = round(total_fit_01 * 100)

        # Apply must cap if enabled and there are gaps
        if self.must_cap_enabled and has_must_gaps:
            total_fit = min(total_fit, int(self.must_cap_value))
            logger.info(f"Applied must cap: {self.must_cap_value}")

        # Ensure bounds
        total_fit = max(0, min(100, total_fit))

        logger.info(
            f"Total fit: {total_fit} "
            f"(must={must_score:.2f}, nice={nice_score:.2f}, "
            f"year={year_score:.2f}, role={role_score:.2f})"
        )
        return total_fit
