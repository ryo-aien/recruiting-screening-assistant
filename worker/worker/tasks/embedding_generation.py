import logging
import uuid
from typing import Any

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from worker.clients.embedding_client import EmbeddingClient, get_embedding_client
from worker.models import Embedding, EmbeddingKind, Extraction
from worker.schemas.extraction_schema import ExtractionResult

logger = logging.getLogger(__name__)


class EmbeddingGenerationTask:
    """Task for generating embeddings for Nice score calculation."""

    def __init__(
        self,
        db: AsyncSession,
        embedding_client: EmbeddingClient | None = None,
    ):
        self.db = db
        self.embedding_client = embedding_client or get_embedding_client()

    async def execute(self, candidate_id: str) -> list[str]:
        """Generate embeddings for candidate and nice requirements.

        Args:
            candidate_id: Candidate ID to process

        Returns:
            List of generated embedding IDs
        """
        logger.info(f"Starting embedding generation for candidate {candidate_id}")

        # Get extraction data
        extraction = await self._get_extraction(candidate_id)

        # Delete existing embeddings
        await self._delete_existing_embeddings(candidate_id)

        embedding_ids = []

        # Generate candidate summary embedding
        candidate_text = self._build_candidate_text(extraction)
        if candidate_text:
            candidate_vector = await self.embedding_client.create_embedding(candidate_text)
            embedding_id = await self._save_embedding(
                candidate_id=candidate_id,
                kind=EmbeddingKind.CANDIDATE_SUMMARY,
                ref_id=None,
                vector=candidate_vector,
            )
            embedding_ids.append(embedding_id)

        # Generate nice requirement embeddings
        job_requirements = extraction.job_requirements_json or {}
        nice_requirements = job_requirements.get("nice", [])

        for nice_req in nice_requirements:
            nice_text = nice_req.get("text", "")
            if nice_text:
                nice_vector = await self.embedding_client.create_embedding(nice_text)
                embedding_id = await self._save_embedding(
                    candidate_id=candidate_id,
                    kind=EmbeddingKind.NICE_REQ,
                    ref_id=nice_req.get("id"),
                    vector=nice_vector,
                )
                embedding_ids.append(embedding_id)

        await self.db.commit()
        logger.info(
            f"Embedding generation completed for candidate {candidate_id}: "
            f"{len(embedding_ids)} embeddings created"
        )
        return embedding_ids

    async def _get_extraction(self, candidate_id: str) -> Extraction:
        """Get extraction for candidate."""
        stmt = select(Extraction).where(Extraction.candidate_id == candidate_id)
        result = await self.db.execute(stmt)
        extraction = result.scalar_one_or_none()
        if not extraction:
            raise ValueError(f"No extraction found for candidate: {candidate_id}")
        return extraction

    async def _delete_existing_embeddings(self, candidate_id: str) -> None:
        """Delete existing embeddings for candidate."""
        stmt = delete(Embedding).where(Embedding.candidate_id == candidate_id)
        await self.db.execute(stmt)

    def _build_candidate_text(self, extraction: Extraction) -> str:
        """Build text for candidate summary embedding."""
        profile = extraction.candidate_profile_json or {}
        parts = []

        # Add skills
        skills = profile.get("skills", [])
        if skills:
            parts.append(f"Skills: {', '.join(skills)}")

        # Add highlights
        highlights = profile.get("highlights", [])
        if highlights:
            parts.append(f"Highlights: {'. '.join(highlights)}")

        # Add roles
        roles = profile.get("roles", [])
        if roles:
            parts.append(f"Roles: {', '.join(roles)}")

        return " | ".join(parts)

    async def _save_embedding(
        self,
        candidate_id: str,
        kind: EmbeddingKind,
        ref_id: str | None,
        vector: list[float],
    ) -> str:
        """Save embedding to database."""
        embedding_id = str(uuid.uuid4())
        embedding = Embedding(
            embedding_id=embedding_id,
            candidate_id=candidate_id,
            kind=kind.value,
            ref_id=ref_id,
            vector=vector,
        )
        self.db.add(embedding)
        return embedding_id
