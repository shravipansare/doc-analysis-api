from pydantic import BaseModel
from typing import List, Optional


class Entity(BaseModel):
    text: str
    type: str  # PERSON, ORGANIZATION, LOCATION, DATE, MONEY, OTHER


class Sentiment(BaseModel):
    label: str  # positive, negative, neutral
    score: float  # -1.0 to 1.0
    explanation: str


class Analysis(BaseModel):
    summary: str
    entities: List[Entity]
    sentiment: Sentiment


class Metadata(BaseModel):
    processing_time_ms: int
    ocr_used: bool
    page_count: Optional[int] = None
    word_count: int


class AnalysisResponse(BaseModel):
    status: str = "success"
    filename: str
    file_type: str
    extracted_text_preview: str
    analysis: Analysis
    metadata: Metadata


class ErrorResponse(BaseModel):
    status: str = "error"
    error_code: str
    message: str


class BatchAnalysisResponse(BaseModel):
    status: str = "success"
    batch_id: str
    results: List[AnalysisResponse]


class QueryRequest(BaseModel):
    query: str


class QueryResponse(BaseModel):
    status: str = "success"
    query: str
    answer: str

