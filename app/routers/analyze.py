import os
import time
import logging
import tempfile
from pathlib import Path

from fastapi import APIRouter, File, Form, UploadFile, HTTPException, Depends
from fastapi.security.api_key import APIKeyHeader

from app.models.schemas import AnalysisResponse, ErrorResponse, Metadata
from app.services.extractor import extract_text
from app.services.ai_analyzer import analyze_text
from app.utils.file_utils import get_file_type, get_supported_extensions

logger = logging.getLogger(__name__)

router = APIRouter()

# --------------------------------------------------------------------------- #
# API Key auth (accepts via header OR form field)
# --------------------------------------------------------------------------- #

api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


def verify_api_key(api_key_header: str = Depends(api_key_header)):
    """Validate service API key from X-API-Key header."""
    service_key = os.getenv("SERVICE_API_KEY", "")

    # If no SERVICE_API_KEY is configured, allow all (dev mode)
    if not service_key:
        return True

    if api_key_header and api_key_header == service_key:
        return True

    raise HTTPException(
        status_code=401,
        detail={
            "status": "error",
            "error_code": "UNAUTHORIZED",
            "message": "Invalid or missing API key. Provide via 'X-API-Key' header.",
        },
    )


# --------------------------------------------------------------------------- #
# Main endpoint
# --------------------------------------------------------------------------- #


@router.post(
    "/analyze",
    response_model=AnalysisResponse,
    summary="Analyze a document (PDF, DOCX, or image)",
    description="""
Upload a document (PDF, DOCX, PNG, JPG, JPEG, TIFF, BMP, WEBP) and receive:
- **Summary**: Concise AI-generated summary
- **Entities**: Named entities (persons, organizations, locations, dates, monetary amounts)
- **Sentiment**: Overall sentiment with score (-1.0 to 1.0)
    """,
    responses={
        200: {"description": "Successful analysis"},
        400: {"description": "Bad request (unsupported format, no text, etc.)"},
        401: {"description": "Unauthorized (invalid API key)"},
        422: {"description": "Validation error"},
        500: {"description": "Internal server error"},
    },
)
async def analyze_document(
    file: UploadFile = File(..., description="Document to analyze (PDF, DOCX, or image)"),
    _: bool = Depends(verify_api_key),
):
    start_time = time.time()
    tmp_path = None

    try:
        # ------------------------------------------------------------------ #
        # 1. Validate file type
        # ------------------------------------------------------------------ #
        filename = file.filename or "unknown"
        file_type = get_file_type(filename)

        if not file_type:
            supported = ", ".join(get_supported_extensions())
            raise HTTPException(
                status_code=400,
                detail={
                    "status": "error",
                    "error_code": "UNSUPPORTED_FORMAT",
                    "message": f"File type not supported. Supported extensions: {supported}",
                },
            )

        # ------------------------------------------------------------------ #
        # 2. Save upload to temp file
        # ------------------------------------------------------------------ #
        suffix = Path(filename).suffix.lower()
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            content = await file.read()
            if len(content) == 0:
                raise HTTPException(
                    status_code=400,
                    detail={
                        "status": "error",
                        "error_code": "EMPTY_FILE",
                        "message": "The uploaded file is empty.",
                    },
                )
            tmp.write(content)
            tmp_path = tmp.name

        logger.info(f"Processing '{filename}' ({file_type}) — {len(content)} bytes")

        # ------------------------------------------------------------------ #
        # 3. Extract text
        # ------------------------------------------------------------------ #
        extract_result = extract_text(tmp_path, file_type)

        if not extract_result.text or len(extract_result.text.strip()) < 10:
            raise HTTPException(
                status_code=400,
                detail={
                    "status": "error",
                    "error_code": "NO_TEXT_EXTRACTED",
                    "message": "Could not extract meaningful text from the document. "
                    "The file may be corrupted, password-protected, or contain only images.",
                },
            )

        # ------------------------------------------------------------------ #
        # 4. AI Analysis via Groq
        # ------------------------------------------------------------------ #
        analysis = analyze_text(extract_result.text)

        # ------------------------------------------------------------------ #
        # 5. Build response
        # ------------------------------------------------------------------ #
        processing_ms = int((time.time() - start_time) * 1000)
        preview = extract_result.text[:500].replace("\n", " ").strip()

        return AnalysisResponse(
            status="success",
            filename=filename,
            file_type=file_type,
            extracted_text_preview=preview,
            analysis=analysis,
            metadata=Metadata(
                processing_time_ms=processing_ms,
                ocr_used=extract_result.ocr_used,
                page_count=extract_result.page_count,
                word_count=extract_result.word_count,
            ),
        )

    except HTTPException:
        raise

    except Exception as e:
        logger.exception(f"Unexpected error processing '{file.filename}': {e}")
        raise HTTPException(
            status_code=500,
            detail={
                "status": "error",
                "error_code": "PROCESSING_ERROR",
                "message": f"An unexpected error occurred: {str(e)}",
            },
        )

    finally:
        # Always clean up temp file
        if tmp_path and os.path.exists(tmp_path):
            try:
                os.unlink(tmp_path)
            except Exception:
                pass
