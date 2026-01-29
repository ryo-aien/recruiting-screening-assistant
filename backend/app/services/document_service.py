import hashlib

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import BadRequestException, NotFoundException
from app.core.storage import StorageService, get_storage
from app.models.candidate import CandidateStatus
from app.models.document import DocumentType
from app.models.jobs_queue import JobType
from app.repositories.candidate_repository import CandidateRepository
from app.repositories.document_repository import DocumentRepository
from app.repositories.queue_repository import QueueRepository
from app.schemas.document import DocumentResponse


class DocumentService:
    """Service for document operations."""

    def __init__(self, db: AsyncSession, storage: StorageService | None = None):
        self.db = db
        self.storage = storage or get_storage()
        self.document_repo = DocumentRepository(db)
        self.candidate_repo = CandidateRepository(db)
        self.queue_repo = QueueRepository(db)

    async def upload_document(
        self,
        candidate_id: str,
        file_content: bytes,
        filename: str,
        doc_type: DocumentType,
    ) -> DocumentResponse:
        """Upload a document for a candidate and queue processing."""
        # Verify candidate exists
        candidate = await self.candidate_repo.get_by_id(candidate_id)
        if not candidate:
            raise NotFoundException(f"Candidate {candidate_id} not found")

        # Validate file type
        ext = filename.lower().split(".")[-1] if "." in filename else ""
        if ext not in ["pdf", "docx", "doc"]:
            raise BadRequestException(f"Unsupported file type: {ext}")

        # Calculate hash for idempotency
        file_hash = hashlib.sha256(file_content).hexdigest()

        # Check if document with same hash already exists
        existing = await self.document_repo.get_by_hash(file_hash)
        if existing and existing.candidate_id == candidate_id:
            return DocumentResponse.model_validate(existing)

        # Save file to storage
        object_uri = await self.storage.save_raw_file(file_content, filename)

        # Create document record
        document = await self.document_repo.create_document(
            candidate_id=candidate_id,
            doc_type=doc_type,
            original_filename=filename,
            object_uri=object_uri,
            file_hash=file_hash,
        )

        # Update candidate status
        await self.candidate_repo.update_status(candidate, CandidateStatus.PROCESSING)

        # Queue text extraction job
        await self.queue_repo.create_job(candidate_id, JobType.TEXT_EXTRACT)

        return DocumentResponse.model_validate(document)

    async def get_document(self, document_id: str) -> DocumentResponse:
        """Get a document by ID."""
        document = await self.document_repo.get_by_id(document_id)
        if not document:
            raise NotFoundException(f"Document {document_id} not found")
        return DocumentResponse.model_validate(document)

    async def list_documents(self, candidate_id: str) -> list[DocumentResponse]:
        """List all documents for a candidate."""
        documents = await self.document_repo.get_by_candidate_id(candidate_id)
        return [DocumentResponse.model_validate(d) for d in documents]

    async def get_document_content(self, document_id: str) -> tuple[bytes, str]:
        """Get document file content and filename."""
        document = await self.document_repo.get_by_id(document_id)
        if not document:
            raise NotFoundException(f"Document {document_id} not found")

        content = await self.storage.read_file(document.object_uri)
        return content, document.original_filename

    async def get_extracted_text(self, document_id: str) -> str | None:
        """Get extracted text for a document."""
        document = await self.document_repo.get_by_id(document_id)
        if not document:
            raise NotFoundException(f"Document {document_id} not found")

        if not document.text_uri:
            return None

        return await self.storage.read_text_file(document.text_uri)
