import logging
import magic

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from worker.extractors.pdf_extractor import PDFExtractor
from worker.extractors.word_extractor import WordExtractor
from worker.storage import StorageService

logger = logging.getLogger(__name__)


class TextExtractionTask:
    """Task for extracting text from uploaded documents."""

    def __init__(self, db: AsyncSession, storage: StorageService):
        self.db = db
        self.storage = storage
        self.pdf_extractor = PDFExtractor()
        self.word_extractor = WordExtractor()

    async def execute(self, candidate_id: str) -> str | None:
        """Extract text from all documents for a candidate.

        Returns the combined text URI or None if no documents.
        """
        logger.info(f"Starting text extraction for candidate {candidate_id}")

        # Get documents for candidate
        from worker.models import Document

        stmt = select(Document).where(Document.candidate_id == candidate_id)
        result = await self.db.execute(stmt)
        documents = list(result.scalars().all())

        if not documents:
            logger.warning(f"No documents found for candidate {candidate_id}")
            return None

        all_text_parts = []

        for doc in documents:
            try:
                # Read raw file
                content = await self.storage.read_raw_file(doc.object_uri)

                # Determine file type
                mime_type = magic.from_buffer(content, mime=True)
                logger.info(f"Processing document {doc.document_id}, type: {mime_type}")

                # Extract text based on file type
                if mime_type == "application/pdf":
                    text = await self.pdf_extractor.extract(content)
                elif mime_type in [
                    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                    "application/msword",
                ]:
                    text = await self.word_extractor.extract(content)
                else:
                    # Try to detect by extension
                    ext = doc.original_filename.lower().split(".")[-1]
                    if ext == "pdf":
                        text = await self.pdf_extractor.extract(content)
                    elif ext in ["docx", "doc"]:
                        text = await self.word_extractor.extract(content)
                    else:
                        logger.warning(f"Unsupported file type: {mime_type}")
                        continue

                # Add document type label
                doc_label = f"[{doc.type.upper()}]"
                all_text_parts.append(f"{doc_label}\n{text}")

                # Save individual document text
                text_uri = await self.storage.save_text_file(text, candidate_id)

                # Update document with text URI
                stmt = (
                    update(Document)
                    .where(Document.document_id == doc.document_id)
                    .values(text_uri=text_uri)
                )
                await self.db.execute(stmt)

                logger.info(f"Extracted text from document {doc.document_id}")

            except Exception as e:
                logger.error(f"Failed to extract text from document {doc.document_id}: {e}")
                raise

        if not all_text_parts:
            raise ValueError("No text could be extracted from any documents")

        # Combine all text and save
        combined_text = "\n\n---\n\n".join(all_text_parts)
        combined_uri = await self.storage.save_text_file(combined_text, candidate_id)

        await self.db.commit()

        logger.info(f"Text extraction completed for candidate {candidate_id}")
        return combined_uri
