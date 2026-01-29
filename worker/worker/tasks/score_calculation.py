import logging
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from worker.models import Embedding, EmbeddingKind, Extraction, Score, ScoreConfig
from worker.scorers.must_scorer import MustScorer
from worker.scorers.nice_scorer import NiceScorer
from worker.scorers.role_scorer import RoleScorer
from worker.scorers.total_fit_calculator import TotalFitCalculator
from worker.scorers.year_scorer import YearScorer

logger = logging.getLogger(__name__)


class ScoreCalculationTask:
    """Task for calculating candidate scores."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.must_scorer = MustScorer()
        self.year_scorer = YearScorer()
        self.role_scorer = RoleScorer()
        self.nice_scorer = NiceScorer()

    async def execute(self, candidate_id: str) -> dict[str, Any]:
        """Calculate all scores for a candidate.

        Args:
            candidate_id: Candidate ID to process

        Returns:
            Score results dictionary
        """
        logger.info(f"Starting score calculation for candidate {candidate_id}")

        # Get extraction data
        extraction = await self._get_extraction(candidate_id)
        job_requirements = extraction.job_requirements_json or {}
        candidate_profile = extraction.candidate_profile_json or {}

        # Get score config
        config = await self._get_score_config()

        # Calculate Must score
        must_score, must_gaps = self.must_scorer.calculate(
            job_requirements, candidate_profile
        )

        # Calculate Year score
        year_score = self.year_scorer.calculate(job_requirements, candidate_profile)

        # Calculate Role score
        self.role_scorer.role_distance = config.role_distance_json
        role_score = self.role_scorer.calculate(job_requirements, candidate_profile)

        # Calculate Nice score using embeddings
        self.nice_scorer.top_n = config.nice_top_n
        candidate_embedding, nice_embeddings = await self._get_embeddings(candidate_id)
        nice_score = self.nice_scorer.calculate(candidate_embedding, nice_embeddings)

        # Calculate total fit
        calculator = TotalFitCalculator(
            weights=config.weights_json,
            must_cap_enabled=config.must_cap_enabled,
            must_cap_value=config.must_cap_value,
        )
        total_fit = calculator.calculate(
            must_score=must_score,
            nice_score=nice_score,
            year_score=year_score,
            role_score=role_score,
            has_must_gaps=len(must_gaps) > 0,
        )

        # Save scores
        await self._save_score(
            candidate_id=candidate_id,
            must_score=must_score,
            nice_score=nice_score,
            year_score=year_score,
            role_score=role_score,
            total_fit=total_fit,
            must_gaps=must_gaps,
            config_version=config.version,
        )

        logger.info(f"Score calculation completed for candidate {candidate_id}")
        return {
            "must_score": must_score,
            "nice_score": nice_score,
            "year_score": year_score,
            "role_score": role_score,
            "total_fit_0_100": total_fit,
            "must_gaps": must_gaps,
        }

    async def _get_extraction(self, candidate_id: str) -> Extraction:
        """Get extraction for candidate."""
        stmt = select(Extraction).where(Extraction.candidate_id == candidate_id)
        result = await self.db.execute(stmt)
        extraction = result.scalar_one_or_none()
        if not extraction:
            raise ValueError(f"No extraction found for candidate: {candidate_id}")
        return extraction

    async def _get_score_config(self) -> ScoreConfig:
        """Get latest score config."""
        stmt = select(ScoreConfig).order_by(ScoreConfig.version.desc()).limit(1)
        result = await self.db.execute(stmt)
        config = result.scalar_one_or_none()
        if not config:
            raise ValueError("No score config found")
        return config

    async def _get_embeddings(
        self, candidate_id: str
    ) -> tuple[list[float] | None, list[tuple[str, list[float]]]]:
        """Get embeddings for scoring."""
        stmt = select(Embedding).where(Embedding.candidate_id == candidate_id)
        result = await self.db.execute(stmt)
        embeddings = list(result.scalars().all())

        candidate_embedding = None
        nice_embeddings = []

        for emb in embeddings:
            if emb.kind == EmbeddingKind.CANDIDATE_SUMMARY.value:
                candidate_embedding = emb.vector
            elif emb.kind == EmbeddingKind.NICE_REQ.value:
                nice_embeddings.append((emb.ref_id, emb.vector))

        return candidate_embedding, nice_embeddings

    async def _save_score(
        self,
        candidate_id: str,
        must_score: float,
        nice_score: float,
        year_score: float,
        role_score: float,
        total_fit: int,
        must_gaps: list[str],
        config_version: int,
    ) -> None:
        """Save score to database."""
        stmt = select(Score).where(Score.candidate_id == candidate_id)
        result = await self.db.execute(stmt)
        existing = result.scalar_one_or_none()

        if existing:
            existing.must_score = must_score
            existing.nice_score = nice_score
            existing.year_score = year_score
            existing.role_score = role_score
            existing.total_fit_0_100 = total_fit
            existing.must_gaps_json = must_gaps
            existing.score_config_version = config_version
        else:
            new_score = Score(
                candidate_id=candidate_id,
                must_score=must_score,
                nice_score=nice_score,
                year_score=year_score,
                role_score=role_score,
                total_fit_0_100=total_fit,
                must_gaps_json=must_gaps,
                score_config_version=config_version,
            )
            self.db.add(new_score)

        await self.db.commit()
