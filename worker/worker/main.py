"""Worker main entry point - polls job queue and processes tasks."""

import asyncio
import logging
import sys
import uuid

from sqlalchemy import select, update

from worker.config import get_settings
from worker.database import AsyncSessionLocal
from worker.models import Candidate, CandidateStatus, JobsQueue, JobType, QueueStatus
from worker.storage import get_storage
from worker.tasks.embedding_generation import EmbeddingGenerationTask
from worker.tasks.explanation_generation import ExplanationGenerationTask
from worker.tasks.llm_extraction import LLMExtractionTask
from worker.tasks.score_calculation import ScoreCalculationTask
from worker.tasks.text_extraction import TextExtractionTask

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger(__name__)

settings = get_settings()


async def get_next_job() -> tuple[JobsQueue | None, asyncio.Lock]:
    """Get the next ready job from queue."""
    async with AsyncSessionLocal() as db:
        stmt = (
            select(JobsQueue)
            .where(JobsQueue.status == QueueStatus.READY.value)
            .order_by(JobsQueue.created_at.asc())
            .limit(1)
            .with_for_update(skip_locked=True)
        )
        result = await db.execute(stmt)
        job = result.scalar_one_or_none()

        if job:
            # Mark as running
            job.status = QueueStatus.RUNNING.value
            job.attempts += 1
            await db.commit()
            await db.refresh(job)

        return job, asyncio.Lock()


async def mark_job_done(queue_id: str) -> None:
    """Mark a job as done."""
    async with AsyncSessionLocal() as db:
        stmt = (
            update(JobsQueue)
            .where(JobsQueue.queue_id == queue_id)
            .values(status=QueueStatus.DONE.value)
        )
        await db.execute(stmt)
        await db.commit()


async def mark_job_failed(queue_id: str, error: str) -> None:
    """Mark a job as failed."""
    async with AsyncSessionLocal() as db:
        stmt = (
            update(JobsQueue)
            .where(JobsQueue.queue_id == queue_id)
            .values(status=QueueStatus.FAILED.value, last_error=error[:1000])
        )
        await db.execute(stmt)
        await db.commit()


async def update_candidate_error(candidate_id: str, error: str) -> None:
    """Update candidate with error status."""
    async with AsyncSessionLocal() as db:
        stmt = (
            update(Candidate)
            .where(Candidate.candidate_id == candidate_id)
            .values(status=CandidateStatus.ERROR.value, error_message=error[:1000])
        )
        await db.execute(stmt)
        await db.commit()


async def enqueue_next_job(candidate_id: str, current_job_type: str) -> None:
    """Enqueue the next job in the pipeline."""
    next_job_map = {
        JobType.TEXT_EXTRACT.value: JobType.LLM_EXTRACT.value,
        JobType.LLM_EXTRACT.value: JobType.EMBED.value,
        JobType.EMBED.value: JobType.SCORE.value,
        JobType.SCORE.value: JobType.EXPLAIN.value,
    }

    next_type = next_job_map.get(current_job_type)
    if next_type:
        async with AsyncSessionLocal() as db:
            new_job = JobsQueue(
                queue_id=str(uuid.uuid4()),
                candidate_id=candidate_id,
                job_type=next_type,
                status=QueueStatus.READY.value,
                attempts=0,
            )
            db.add(new_job)
            await db.commit()
            logger.info(f"Enqueued next job: {next_type} for candidate {candidate_id}")


async def process_job(job: JobsQueue) -> None:
    """Process a single job."""
    logger.info(f"Processing job {job.queue_id}: {job.job_type} for candidate {job.candidate_id}")

    try:
        async with AsyncSessionLocal() as db:
            storage = get_storage()

            if job.job_type == JobType.TEXT_EXTRACT.value:
                task = TextExtractionTask(db, storage)
                await task.execute(job.candidate_id)

            elif job.job_type == JobType.LLM_EXTRACT.value:
                task = LLMExtractionTask(db, storage)
                await task.execute(job.candidate_id)

            elif job.job_type == JobType.EMBED.value:
                task = EmbeddingGenerationTask(db)
                await task.execute(job.candidate_id)

            elif job.job_type == JobType.SCORE.value:
                task = ScoreCalculationTask(db)
                await task.execute(job.candidate_id)

            elif job.job_type == JobType.EXPLAIN.value:
                task = ExplanationGenerationTask(db)
                await task.execute(job.candidate_id)

            else:
                raise ValueError(f"Unknown job type: {job.job_type}")

        # Mark job as done
        await mark_job_done(job.queue_id)
        logger.info(f"Job {job.queue_id} completed successfully")

        # Enqueue next job in pipeline
        await enqueue_next_job(job.candidate_id, job.job_type)

    except Exception as e:
        error_msg = str(e)
        logger.error(f"Job {job.queue_id} failed: {error_msg}")

        # Mark job as failed
        await mark_job_failed(job.queue_id, error_msg)

        # Update candidate status if max retries exceeded
        if job.attempts >= settings.max_retries:
            logger.error(
                f"Max retries ({settings.max_retries}) exceeded for job {job.queue_id}"
            )
            await update_candidate_error(job.candidate_id, error_msg)


async def poll_loop() -> None:
    """Main polling loop."""
    logger.info(
        f"Worker started. Polling interval: {settings.poll_interval}s, "
        f"Max retries: {settings.max_retries}"
    )

    while True:
        try:
            job, _ = await get_next_job()

            if job:
                await process_job(job)
            else:
                # No jobs available, wait before polling again
                await asyncio.sleep(settings.poll_interval)

        except Exception as e:
            logger.error(f"Error in poll loop: {e}")
            await asyncio.sleep(settings.poll_interval)


def main() -> None:
    """Main entry point."""
    logger.info("Starting worker...")
    asyncio.run(poll_loop())


if __name__ == "__main__":
    main()
