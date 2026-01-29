from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.audit_event import AuditEvent
from app.repositories.audit_repository import AuditRepository


class AuditService:
    """Service for audit log operations."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.audit_repo = AuditRepository(db)

    async def log_event(
        self,
        action: str,
        entity_type: str,
        entity_id: str | None = None,
        actor_id: str | None = None,
        payload: dict[str, Any] | None = None,
    ) -> AuditEvent:
        """Log an audit event."""
        return await self.audit_repo.log_event(
            action=action,
            entity_type=entity_type,
            entity_id=entity_id,
            actor_id=actor_id,
            payload=payload,
        )

    async def get_events_by_entity(
        self,
        entity_type: str,
        entity_id: str | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> list[AuditEvent]:
        """Get audit events for an entity."""
        return await self.audit_repo.get_by_entity(
            entity_type=entity_type,
            entity_id=entity_id,
            limit=limit,
            offset=offset,
        )
