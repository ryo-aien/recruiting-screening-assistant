import uuid
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.audit_event import AuditEvent
from app.repositories.base import BaseRepository


class AuditRepository(BaseRepository[AuditEvent]):
    """Repository for audit event operations."""

    def __init__(self, db: AsyncSession):
        super().__init__(AuditEvent, db)

    async def get_by_entity(
        self,
        entity_type: str,
        entity_id: str | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> list[AuditEvent]:
        """Get audit events by entity type and optionally entity ID."""
        stmt = select(AuditEvent).where(AuditEvent.entity_type == entity_type)
        if entity_id:
            stmt = stmt.where(AuditEvent.entity_id == entity_id)
        stmt = stmt.order_by(AuditEvent.created_at.desc()).limit(limit).offset(offset)
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def log_event(
        self,
        action: str,
        entity_type: str,
        entity_id: str | None = None,
        actor_id: str | None = None,
        payload: dict[str, Any] | None = None,
    ) -> AuditEvent:
        """Log a new audit event."""
        event = AuditEvent(
            event_id=str(uuid.uuid4()),
            actor_id=actor_id,
            action=action,
            entity_type=entity_type,
            entity_id=entity_id,
            payload_json=payload,
        )
        return await self.create(event)
