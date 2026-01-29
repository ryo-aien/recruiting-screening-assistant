from datetime import datetime

from pydantic import BaseModel, Field

from app.models.document import DocumentType


class DocumentCreate(BaseModel):
    """Schema for creating a new document (metadata only, file handled separately)."""

    type: DocumentType = Field(..., description="Type of document: resume or cv")


class DocumentResponse(BaseModel):
    """Schema for document response."""

    document_id: str
    candidate_id: str
    type: DocumentType
    original_filename: str
    object_uri: str
    text_uri: str | None
    file_hash: str | None
    created_at: datetime

    model_config = {"from_attributes": True}
