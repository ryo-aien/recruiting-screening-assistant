from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundException
from app.models.decision import DecisionType
from app.repositories.audit_repository import AuditRepository
from app.repositories.candidate_repository import CandidateRepository
from app.repositories.decision_repository import DecisionRepository
from app.schemas.decision import DecisionCreate, DecisionResponse


class DecisionService:
    """Service for decision operations."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.decision_repo = DecisionRepository(db)
        self.candidate_repo = CandidateRepository(db)
        self.audit_repo = AuditRepository(db)

    async def create_decision(
        self,
        candidate_id: str,
        data: DecisionCreate,
    ) -> DecisionResponse:
        """Create a decision for a candidate."""
        # Verify candidate exists
        candidate = await self.candidate_repo.get_by_id(candidate_id)
        if not candidate:
            raise NotFoundException(f"Candidate {candidate_id} not found")

        # Create decision
        decision = await self.decision_repo.create_decision(
            candidate_id=candidate_id,
            decision=data.decision,
            reason=data.reason,
            decided_by=data.decided_by,
        )

        # Log audit event
        await self.audit_repo.log_event(
            action="decision_created",
            entity_type="candidate",
            entity_id=candidate_id,
            actor_id=data.decided_by,
            payload={
                "decision": data.decision.value,
                "reason": data.reason,
            },
        )

        return DecisionResponse.model_validate(decision)

    async def get_decisions(self, candidate_id: str) -> list[DecisionResponse]:
        """Get all decisions for a candidate."""
        decisions = await self.decision_repo.get_by_candidate_id(candidate_id)
        return [DecisionResponse.model_validate(d) for d in decisions]

    async def get_latest_decision(self, candidate_id: str) -> DecisionResponse | None:
        """Get the latest decision for a candidate."""
        decision = await self.decision_repo.get_latest_by_candidate_id(candidate_id)
        if decision:
            return DecisionResponse.model_validate(decision)
        return None
