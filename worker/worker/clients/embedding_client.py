import logging
from typing import Any

import numpy as np
from openai import AsyncOpenAI

from worker.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


class EmbeddingClient:
    """Client for OpenAI Embeddings API."""

    def __init__(self, api_key: str | None = None):
        self.api_key = api_key or settings.openai_api_key
        self._client: AsyncOpenAI | None = None

    @property
    def client(self) -> AsyncOpenAI:
        if self._client is None:
            if not self.api_key:
                raise ValueError("OpenAI API key is not configured")
            self._client = AsyncOpenAI(api_key=self.api_key)
        return self._client

    async def create_embedding(self, text: str, model: str | None = None) -> list[float]:
        """Create embedding for a single text.

        Args:
            text: Text to embed
            model: Model to use

        Returns:
            Embedding vector as list of floats
        """
        model = model or settings.embedding_model
        logger.info(f"Creating embedding with model {model}")

        try:
            response = await self.client.embeddings.create(
                model=model,
                input=text,
            )
            return response.data[0].embedding

        except Exception as e:
            logger.error(f"Embedding creation failed: {e}")
            raise

    async def create_embeddings_batch(
        self, texts: list[str], model: str | None = None
    ) -> list[list[float]]:
        """Create embeddings for multiple texts in batch.

        Args:
            texts: List of texts to embed
            model: Model to use

        Returns:
            List of embedding vectors
        """
        model = model or settings.embedding_model
        logger.info(f"Creating {len(texts)} embeddings with model {model}")

        try:
            response = await self.client.embeddings.create(
                model=model,
                input=texts,
            )
            # Sort by index to maintain order
            sorted_embeddings = sorted(response.data, key=lambda x: x.index)
            return [e.embedding for e in sorted_embeddings]

        except Exception as e:
            logger.error(f"Batch embedding creation failed: {e}")
            raise

    @staticmethod
    def cosine_similarity(vec1: list[float], vec2: list[float]) -> float:
        """Calculate cosine similarity between two vectors.

        Args:
            vec1: First vector
            vec2: Second vector

        Returns:
            Cosine similarity (0 to 1)
        """
        a = np.array(vec1)
        b = np.array(vec2)
        return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))


class MockEmbeddingClient(EmbeddingClient):
    """Mock client for testing without API key."""

    def __init__(self):
        super().__init__(api_key="mock-key")

    async def create_embedding(self, text: str, model: str | None = None) -> list[float]:
        """Return mock embedding (random but deterministic based on text hash)."""
        logger.warning("Using mock embedding client - returning placeholder embedding")
        np.random.seed(hash(text) % (2**32))
        return list(np.random.randn(1536).astype(float))

    async def create_embeddings_batch(
        self, texts: list[str], model: str | None = None
    ) -> list[list[float]]:
        """Return mock embeddings for batch."""
        logger.warning("Using mock embedding client - returning placeholder embeddings")
        return [await self.create_embedding(text) for text in texts]


def get_embedding_client() -> EmbeddingClient:
    """Get embedding client, falling back to mock if no API key."""
    if settings.openai_api_key:
        return EmbeddingClient()
    logger.warning("No OpenAI API key configured, using mock embedding client")
    return MockEmbeddingClient()
