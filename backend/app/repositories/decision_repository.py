import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.decision import Decision, DecisionType
from app.repositories.base import BaseRepository


class DecisionRepository(BaseRepository[Decision]):
    """Repository for decision operations."""

    def __init__(self, db: AsyncSession):
        super().__init__(Decision, db)

    async def get_by_id(self, decision_id: str) -> Decision | None:
        """Get a decision by ID."""
        stmt = select(Decision).where(Decision.decision_id == decision_id)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_candidate_id(self, candidate_id: str) -> list[Decision]:
        """Get all decisions for a candidate."""
        stmt = (
            select(Decision)
            .where(Decision.candidate_id == candidate_id)
            .order_by(Decision.decided_at.desc())
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def get_latest_by_candidate_id(self, candidate_id: str) -> Decision | None:
        """Get the latest decision for a candidate."""
        stmt = (
            select(Decision)
            .where(Decision.candidate_id == candidate_id)
            .order_by(Decision.decided_at.desc())
            .limit(1)
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def create_decision(
        self,
        candidate_id: str,
        decision: DecisionType,
        reason: str | None = None,
        decided_by: str | None = None,
    ) -> Decision:
        """Create a new decision."""
        dec = Decision(
            decision_id=str(uuid.uuid4()),
            candidate_id=candidate_id,
            decision=decision,
            reason=reason,
            decided_by=decided_by,
        )
        return await self.create(dec)
