from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.score_config import ScoreConfig
from app.repositories.base import BaseRepository


class ScoreConfigRepository(BaseRepository[ScoreConfig]):
    """Repository for score config operations."""

    def __init__(self, db: AsyncSession):
        super().__init__(ScoreConfig, db)

    async def get_latest(self) -> ScoreConfig | None:
        """Get the latest score config."""
        stmt = select(ScoreConfig).order_by(ScoreConfig.version.desc()).limit(1)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_version(self, version: int) -> ScoreConfig | None:
        """Get score config by version."""
        stmt = select(ScoreConfig).where(ScoreConfig.version == version)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def create_new_version(
        self,
        weights_json: dict[str, float],
        must_cap_enabled: bool,
        must_cap_value: float,
        nice_top_n: int,
        role_distance_json: dict[str, dict[str, float]],
    ) -> ScoreConfig:
        """Create a new score config version."""
        config = ScoreConfig(
            weights_json=weights_json,
            must_cap_enabled=must_cap_enabled,
            must_cap_value=must_cap_value,
            nice_top_n=nice_top_n,
            role_distance_json=role_distance_json,
        )
        return await self.create(config)
