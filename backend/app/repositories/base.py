from typing import Any, Generic, TypeVar

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import Base

ModelType = TypeVar("ModelType", bound=Base)


class BaseRepository(Generic[ModelType]):
    """Base repository with common CRUD operations."""

    def __init__(self, model: type[ModelType], db: AsyncSession):
        self.model = model
        self.db = db

    async def get_by_id(self, id_value: Any, id_field: str = "id") -> ModelType | None:
        """Get a single record by ID."""
        stmt = select(self.model).where(getattr(self.model, id_field) == id_value)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_all(self, limit: int = 100, offset: int = 0) -> list[ModelType]:
        """Get all records with pagination."""
        stmt = select(self.model).limit(limit).offset(offset)
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def create(self, obj: ModelType) -> ModelType:
        """Create a new record."""
        self.db.add(obj)
        await self.db.flush()
        await self.db.refresh(obj)
        return obj

    async def update(self, obj: ModelType, update_data: dict[str, Any]) -> ModelType:
        """Update an existing record."""
        for key, value in update_data.items():
            if hasattr(obj, key):
                setattr(obj, key, value)
        await self.db.flush()
        await self.db.refresh(obj)
        return obj

    async def delete(self, obj: ModelType) -> bool:
        """Delete a record."""
        await self.db.delete(obj)
        await self.db.flush()
        return True
