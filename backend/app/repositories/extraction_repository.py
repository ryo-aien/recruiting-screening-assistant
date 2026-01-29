from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.extraction import Extraction
from app.repositories.base import BaseRepository


class ExtractionRepository(BaseRepository[Extraction]):
    """Repository for extraction operations."""

    def __init__(self, db: AsyncSession):
        super().__init__(Extraction, db)

    async def get_by_candidate_id(self, candidate_id: str) -> Extraction | None:
        """Get extraction by candidate ID."""
        stmt = select(Extraction).where(Extraction.candidate_id == candidate_id)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def create_or_update(
        self,
        candidate_id: str,
        job_requirements_json: dict[str, Any] | None,
        candidate_profile_json: dict[str, Any] | None,
        evidence_json: dict[str, Any] | None,
        llm_model: str | None = None,
        extract_version: str | None = None,
    ) -> Extraction:
        """Create or update extraction for a candidate."""
        existing = await self.get_by_candidate_id(candidate_id)
        if existing:
            return await self.update(
                existing,
                {
                    "job_requirements_json": job_requirements_json,
                    "candidate_profile_json": candidate_profile_json,
                    "evidence_json": evidence_json,
                    "llm_model": llm_model,
                    "extract_version": extract_version,
                },
            )
        else:
            extraction = Extraction(
                candidate_id=candidate_id,
                job_requirements_json=job_requirements_json,
                candidate_profile_json=candidate_profile_json,
                evidence_json=evidence_json,
                llm_model=llm_model,
                extract_version=extract_version,
            )
            return await self.create(extraction)
