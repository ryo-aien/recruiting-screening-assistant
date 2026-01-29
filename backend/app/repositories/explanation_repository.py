from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.explanation import Explanation
from app.repositories.base import BaseRepository


class ExplanationRepository(BaseRepository[Explanation]):
    """Repository for explanation operations."""

    def __init__(self, db: AsyncSession):
        super().__init__(Explanation, db)

    async def get_by_candidate_id(self, candidate_id: str) -> Explanation | None:
        """Get explanation by candidate ID."""
        stmt = select(Explanation).where(Explanation.candidate_id == candidate_id)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def create_or_update(
        self,
        candidate_id: str,
        explanation_json: dict[str, Any],
    ) -> Explanation:
        """Create or update explanation for a candidate."""
        existing = await self.get_by_candidate_id(candidate_id)
        if existing:
            return await self.update(existing, {"explanation_json": explanation_json})
        else:
            explanation = Explanation(
                candidate_id=candidate_id,
                explanation_json=explanation_json,
            )
            return await self.create(explanation)
