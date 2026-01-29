import logging
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from worker.clients.openai_client import OpenAIClient, get_openai_client
from worker.config import get_settings
from worker.models import Candidate, Document, Extraction, Job
from worker.prompts.extraction_prompt import ExtractionPrompt
from worker.schemas.extraction_schema import ExtractionResult
from worker.storage import StorageService

logger = logging.getLogger(__name__)
settings = get_settings()


class LLMExtractionTask:
    """Task for extracting structured data using LLM."""

    def __init__(
        self,
        db: AsyncSession,
        storage: StorageService,
        openai_client: OpenAIClient | None = None,
    ):
        self.db = db
        self.storage = storage
        self.openai_client = openai_client or get_openai_client()

    async def execute(self, candidate_id: str) -> ExtractionResult:
        """Extract structured data from candidate documents.

        Args:
            candidate_id: Candidate ID to process

        Returns:
            Extraction result
        """
        logger.info(f"Starting LLM extraction for candidate {candidate_id}")

        # Get candidate and job
        candidate = await self._get_candidate(candidate_id)
        job = await self._get_job(candidate.job_id)

        # Get extracted text from documents
        resume_text = await self._get_extracted_text(candidate_id)

        # Call LLM for extraction
        user_prompt = ExtractionPrompt.format_user_prompt(
            job_text=job.job_text_raw,
            resume_text=resume_text,
        )

        result_dict = await self.openai_client.extract_structured(
            system_prompt=ExtractionPrompt.SYSTEM_PROMPT,
            user_prompt=user_prompt,
            response_format={"type": "json_object"},
        )

        # Parse and validate result
        extraction = ExtractionResult.from_dict(result_dict)

        # Save to database
        await self._save_extraction(candidate_id, extraction)

        logger.info(f"LLM extraction completed for candidate {candidate_id}")
        return extraction

    async def _get_candidate(self, candidate_id: str) -> Candidate:
        """Get candidate by ID."""
        stmt = select(Candidate).where(Candidate.candidate_id == candidate_id)
        result = await self.db.execute(stmt)
        candidate = result.scalar_one_or_none()
        if not candidate:
            raise ValueError(f"Candidate not found: {candidate_id}")
        return candidate

    async def _get_job(self, job_id: str) -> Job:
        """Get job by ID."""
        stmt = select(Job).where(Job.job_id == job_id)
        result = await self.db.execute(stmt)
        job = result.scalar_one_or_none()
        if not job:
            raise ValueError(f"Job not found: {job_id}")
        return job

    async def _get_extracted_text(self, candidate_id: str) -> str:
        """Get combined extracted text for candidate."""
        stmt = select(Document).where(
            Document.candidate_id == candidate_id,
            Document.text_uri.isnot(None),
        )
        result = await self.db.execute(stmt)
        documents = list(result.scalars().all())

        if not documents:
            raise ValueError(f"No extracted text found for candidate: {candidate_id}")

        text_parts = []
        for doc in documents:
            if doc.text_uri:
                text = await self.storage.read_text_file(doc.text_uri)
                text_parts.append(f"[{doc.type.upper()}]\n{text}")

        return "\n\n---\n\n".join(text_parts)

    async def _save_extraction(
        self, candidate_id: str, extraction: ExtractionResult
    ) -> None:
        """Save extraction result to database."""
        # Check if extraction exists
        stmt = select(Extraction).where(Extraction.candidate_id == candidate_id)
        result = await self.db.execute(stmt)
        existing = result.scalar_one_or_none()

        if existing:
            existing.job_requirements_json = extraction.job_requirements.model_dump()
            existing.candidate_profile_json = extraction.candidate_profile.model_dump()
            existing.evidence_json = extraction.evidence.model_dump()
            existing.llm_model = settings.llm_model
            existing.extract_version = "v1"
        else:
            new_extraction = Extraction(
                candidate_id=candidate_id,
                job_requirements_json=extraction.job_requirements.model_dump(),
                candidate_profile_json=extraction.candidate_profile.model_dump(),
                evidence_json=extraction.evidence.model_dump(),
                llm_model=settings.llm_model,
                extract_version="v1",
            )
            self.db.add(new_extraction)

        await self.db.commit()
