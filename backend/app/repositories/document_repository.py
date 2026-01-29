import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.document import Document, DocumentType
from app.repositories.base import BaseRepository


class DocumentRepository(BaseRepository[Document]):
    """Repository for document operations."""

    def __init__(self, db: AsyncSession):
        super().__init__(Document, db)

    async def get_by_id(self, document_id: str) -> Document | None:
        """Get a document by ID."""
        stmt = select(Document).where(Document.document_id == document_id)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_candidate_id(self, candidate_id: str) -> list[Document]:
        """Get all documents for a candidate."""
        stmt = (
            select(Document)
            .where(Document.candidate_id == candidate_id)
            .order_by(Document.created_at.desc())
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def get_by_hash(self, file_hash: str) -> Document | None:
        """Get a document by file hash (for idempotency)."""
        stmt = select(Document).where(Document.file_hash == file_hash)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def create_document(
        self,
        candidate_id: str,
        doc_type: DocumentType,
        original_filename: str,
        object_uri: str,
        file_hash: str | None = None,
    ) -> Document:
        """Create a new document."""
        document = Document(
            document_id=str(uuid.uuid4()),
            candidate_id=candidate_id,
            type=doc_type,
            original_filename=original_filename,
            object_uri=object_uri,
            file_hash=file_hash,
        )
        return await self.create(document)

    async def update_text_uri(self, document: Document, text_uri: str) -> Document:
        """Update the text URI after extraction."""
        return await self.update(document, {"text_uri": text_uri})
