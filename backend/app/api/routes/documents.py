from fastapi import APIRouter, Depends, File, Form, UploadFile, status
from fastapi.responses import Response
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.document import DocumentType
from app.schemas.document import DocumentResponse
from app.services.document_service import DocumentService

router = APIRouter()


@router.post(
    "/candidates/{candidate_id}/documents",
    response_model=DocumentResponse,
    status_code=status.HTTP_201_CREATED,
)
async def upload_document(
    candidate_id: str,
    file: UploadFile = File(...),
    type: DocumentType = Form(...),
    db: AsyncSession = Depends(get_db),
) -> DocumentResponse:
    """Upload a document for a candidate and start processing."""
    service = DocumentService(db)
    content = await file.read()
    return await service.upload_document(
        candidate_id=candidate_id,
        file_content=content,
        filename=file.filename or "document",
        doc_type=type,
    )


@router.get("/candidates/{candidate_id}/documents", response_model=list[DocumentResponse])
async def list_documents(
    candidate_id: str,
    db: AsyncSession = Depends(get_db),
) -> list[DocumentResponse]:
    """List all documents for a candidate."""
    service = DocumentService(db)
    return await service.list_documents(candidate_id)


@router.get("/documents/{document_id}", response_model=DocumentResponse)
async def get_document(
    document_id: str,
    db: AsyncSession = Depends(get_db),
) -> DocumentResponse:
    """Get document metadata."""
    service = DocumentService(db)
    return await service.get_document(document_id)


@router.get("/documents/{document_id}/download")
async def download_document(
    document_id: str,
    db: AsyncSession = Depends(get_db),
) -> Response:
    """Download the original document file."""
    service = DocumentService(db)
    content, filename = await service.get_document_content(document_id)

    # Determine content type
    ext = filename.lower().split(".")[-1] if "." in filename else ""
    content_types = {
        "pdf": "application/pdf",
        "docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "doc": "application/msword",
    }
    content_type = content_types.get(ext, "application/octet-stream")

    return Response(
        content=content,
        media_type=content_type,
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@router.get("/documents/{document_id}/text")
async def get_document_text(
    document_id: str,
    db: AsyncSession = Depends(get_db),
) -> dict:
    """Get extracted text content for a document."""
    service = DocumentService(db)
    text = await service.get_extracted_text(document_id)
    return {"text": text}
