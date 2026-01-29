import logging
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from worker.clients.openai_client import OpenAIClient, get_openai_client
from worker.models import Candidate, CandidateStatus, Explanation, Extraction, Score
from worker.prompts.explanation_prompt import ExplanationPrompt
from worker.schemas.explanation_schema import ExplanationResult

logger = logging.getLogger(__name__)


class ExplanationGenerationTask:
    """Task for generating explanations using LLM."""

    def __init__(
        self,
        db: AsyncSession,
        openai_client: OpenAIClient | None = None,
    ):
        self.db = db
        self.openai_client = openai_client or get_openai_client()

    async def execute(self, candidate_id: str) -> ExplanationResult:
        """Generate explanation for candidate scores.

        Args:
            candidate_id: Candidate ID to process

        Returns:
            Explanation result
        """
        logger.info(f"Starting explanation generation for candidate {candidate_id}")

        # Get required data
        extraction = await self._get_extraction(candidate_id)
        score = await self._get_score(candidate_id)

        job_requirements = extraction.job_requirements_json or {}
        candidate_profile = extraction.candidate_profile_json or {}
        evidence = extraction.evidence_json or {}

        scores_dict = {
            "must_score": score.must_score,
            "nice_score": score.nice_score,
            "year_score": score.year_score,
            "role_score": score.role_score,
            "total_fit_0_100": score.total_fit_0_100,
            "must_gaps": score.must_gaps_json or [],
        }

        # Generate explanation
        user_prompt = ExplanationPrompt.format_user_prompt(
            job_requirements=job_requirements,
            candidate_profile=candidate_profile,
            scores=scores_dict,
            evidence=evidence,
        )

        result_dict = await self.openai_client.generate_explanation(
            system_prompt=ExplanationPrompt.SYSTEM_PROMPT,
            user_prompt=user_prompt,
        )

        explanation = ExplanationResult.from_dict(result_dict)

        # Save explanation
        await self._save_explanation(candidate_id, explanation)

        # Update candidate status to DONE
        await self._update_candidate_status(candidate_id, CandidateStatus.DONE)

        logger.info(f"Explanation generation completed for candidate {candidate_id}")
        return explanation

    async def _get_extraction(self, candidate_id: str) -> Extraction:
        """Get extraction for candidate."""
        stmt = select(Extraction).where(Extraction.candidate_id == candidate_id)
        result = await self.db.execute(stmt)
        extraction = result.scalar_one_or_none()
        if not extraction:
            raise ValueError(f"No extraction found for candidate: {candidate_id}")
        return extraction

    async def _get_score(self, candidate_id: str) -> Score:
        """Get score for candidate."""
        stmt = select(Score).where(Score.candidate_id == candidate_id)
        result = await self.db.execute(stmt)
        score = result.scalar_one_or_none()
        if not score:
            raise ValueError(f"No score found for candidate: {candidate_id}")
        return score

    async def _save_explanation(
        self, candidate_id: str, explanation: ExplanationResult
    ) -> None:
        """Save explanation to database."""
        stmt = select(Explanation).where(Explanation.candidate_id == candidate_id)
        result = await self.db.execute(stmt)
        existing = result.scalar_one_or_none()

        explanation_json = {
            "summary": explanation.summary,
            "strengths": explanation.strengths,
            "concerns": explanation.concerns,
            "unknowns": explanation.unknowns,
            "must_gaps": explanation.must_gaps,
        }

        if existing:
            existing.explanation_json = explanation_json
        else:
            new_explanation = Explanation(
                candidate_id=candidate_id,
                explanation_json=explanation_json,
            )
            self.db.add(new_explanation)

        await self.db.commit()

    async def _update_candidate_status(
        self, candidate_id: str, status: CandidateStatus
    ) -> None:
        """Update candidate status."""
        stmt = select(Candidate).where(Candidate.candidate_id == candidate_id)
        result = await self.db.execute(stmt)
        candidate = result.scalar_one_or_none()
        if candidate:
            candidate.status = status.value
            await self.db.commit()
