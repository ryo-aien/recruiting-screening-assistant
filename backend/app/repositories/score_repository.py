from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.score import Score
from app.repositories.base import BaseRepository


class ScoreRepository(BaseRepository[Score]):
    """Repository for score operations."""

    def __init__(self, db: AsyncSession):
        super().__init__(Score, db)

    async def get_by_candidate_id(self, candidate_id: str) -> Score | None:
        """Get score by candidate ID."""
        stmt = select(Score).where(Score.candidate_id == candidate_id)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def create_or_update(
        self,
        candidate_id: str,
        must_score: float,
        nice_score: float,
        year_score: float,
        role_score: float,
        total_fit_0_100: int,
        must_gaps_json: list[str] | None,
        score_config_version: int,
    ) -> Score:
        """Create or update score for a candidate."""
        existing = await self.get_by_candidate_id(candidate_id)
        if existing:
            return await self.update(
                existing,
                {
                    "must_score": must_score,
                    "nice_score": nice_score,
                    "year_score": year_score,
                    "role_score": role_score,
                    "total_fit_0_100": total_fit_0_100,
                    "must_gaps_json": must_gaps_json,
                    "score_config_version": score_config_version,
                },
            )
        else:
            score = Score(
                candidate_id=candidate_id,
                must_score=must_score,
                nice_score=nice_score,
                year_score=year_score,
                role_score=role_score,
                total_fit_0_100=total_fit_0_100,
                must_gaps_json=must_gaps_json,
                score_config_version=score_config_version,
            )
            return await self.create(score)
