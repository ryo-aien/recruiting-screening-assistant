from fastapi import HTTPException, status


class NotFoundException(HTTPException):
    """Raised when a resource is not found."""

    def __init__(self, detail: str = "Resource not found"):
        super().__init__(status_code=status.HTTP_404_NOT_FOUND, detail=detail)


class BadRequestException(HTTPException):
    """Raised for invalid requests."""

    def __init__(self, detail: str = "Bad request"):
        super().__init__(status_code=status.HTTP_400_BAD_REQUEST, detail=detail)


class ConflictException(HTTPException):
    """Raised when there's a conflict with existing data."""

    def __init__(self, detail: str = "Conflict"):
        super().__init__(status_code=status.HTTP_409_CONFLICT, detail=detail)


class ProcessingException(HTTPException):
    """Raised when processing fails."""

    def __init__(self, detail: str = "Processing failed"):
        super().__init__(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=detail)


class StorageException(Exception):
    """Raised when storage operations fail."""

    pass


class ExtractionException(Exception):
    """Raised when text extraction fails."""

    pass


class LLMException(Exception):
    """Raised when LLM operations fail."""

    pass
