"""Nice-to-have requirements scorer using embeddings."""

import logging
from typing import Any

from worker.clients.embedding_client import EmbeddingClient

logger = logging.getLogger(__name__)


class NiceScorer:
    """Calculate Nice score using embedding similarity."""

    def __init__(self, top_n: int = 3):
        self.top_n = top_n

    def calculate(
        self,
        candidate_embedding: list[float] | None,
        nice_embeddings: list[tuple[str, list[float]]],
    ) -> float:
        """Calculate Nice score using cosine similarity.

        Args:
            candidate_embedding: Candidate summary embedding vector
            nice_embeddings: List of (nice_id, embedding) tuples

        Returns:
            Score between 0 and 1
        """
        if not candidate_embedding or not nice_embeddings:
            logger.info("No embeddings available for Nice score, returning 0")
            return 0.0

        # Calculate similarities
        similarities = []
        for nice_id, nice_vector in nice_embeddings:
            sim = EmbeddingClient.cosine_similarity(candidate_embedding, nice_vector)
            similarities.append((nice_id, sim))

        # Sort by similarity descending
        similarities.sort(key=lambda x: x[1], reverse=True)

        # Take top N
        top_similarities = similarities[: self.top_n]

        if not top_similarities:
            return 0.0

        # Average of top N
        score = sum(sim for _, sim in top_similarities) / len(top_similarities)

        # Normalize to 0-1 range (cosine similarity can be negative)
        score = max(0.0, min(1.0, (score + 1) / 2))

        logger.info(
            f"Nice score: {score:.2f} (top {len(top_similarities)} similarities)"
        )
        return score
