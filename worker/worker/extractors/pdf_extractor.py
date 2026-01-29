import io
import logging

from pypdf import PdfReader

logger = logging.getLogger(__name__)


class PDFExtractor:
    """Extract text from PDF files."""

    async def extract(self, content: bytes) -> str:
        """Extract text from PDF content.

        Args:
            content: PDF file content as bytes

        Returns:
            Extracted text

        Raises:
            Exception: If extraction fails
        """
        try:
            pdf_file = io.BytesIO(content)
            reader = PdfReader(pdf_file)

            text_parts = []
            for page_num, page in enumerate(reader.pages, 1):
                try:
                    page_text = page.extract_text()
                    if page_text:
                        text_parts.append(f"--- Page {page_num} ---\n{page_text}")
                except Exception as e:
                    logger.warning(f"Failed to extract page {page_num}: {e}")
                    continue

            if not text_parts:
                raise ValueError("No text could be extracted from PDF")

            return "\n\n".join(text_parts)

        except Exception as e:
            logger.error(f"PDF extraction failed: {e}")
            raise


def get_pdf_extractor() -> PDFExtractor:
    return PDFExtractor()
