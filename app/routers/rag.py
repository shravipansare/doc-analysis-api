import logging
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security.api_key import APIKeyHeader

from app.models.schemas import QueryRequest, QueryResponse
from app.services.rag_service import query_documents
from app.services.ai_analyzer import generate_rag_response
from app.routers.analyze import verify_api_key

logger = logging.getLogger(__name__)

router = APIRouter()

@router.post(
    "/query",
    response_model=QueryResponse,
    summary="Query indexed documents (RAG)",
    description="Ask questions about the uploaded documents. Ensure documents have been previously uploaded and indexed.",
    responses={
        200: {"description": "Successful query"},
        401: {"description": "Unauthorized"},
        500: {"description": "Internal server error"},
    },
)
async def query_rag(
    request: QueryRequest,
    _: bool = Depends(verify_api_key),
):
    try:
        # Retrieve context from Chroma
        chunks = query_documents(request.query, top_k=5)
        
        # Generate answer using Groq
        answer = generate_rag_response(chunks, request.query)
        
        return QueryResponse(
            status="success",
            query=request.query,
            answer=answer
        )
    except Exception as e:
        logger.exception(f"Error querying RAG: {e}")
        raise HTTPException(
            status_code=500,
            detail={
                "status": "error",
                "error_code": "RAG_QUERY_ERROR",
                "message": f"Failed to perform document query: {str(e)}"
            }
        )
