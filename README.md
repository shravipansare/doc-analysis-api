# Document Analysis API

A professional document processing engine that extracts and analyzes content from PDF, DOCX, and image formats. This project combines traditional OCR techniques with large language models to provide structured insights from unstructured documents.

## Project Overview

This API was designed to solve the challenge of extracting consistent, structured data from diverse document formats. It implements a multi-stage pipeline:
1.  **Direct Extraction**: Leveraging native parsers for digital-first documents.
2.  **OCR Fallback**: Using Tesseract OCR with advanced image preprocessing for scanned documents and images.
3.  **Semantic Analysis**: Utilizing Groq's high-speed LPU inference with the `llama-3.3-70b-versatile` model to generate summaries, extract entities, and evaluate sentiment.

## Technical Decisions

- **FastAPI**: Selected for its asynchronous capabilities and native support for OpenAPI documentation, ensuring high performance under concurrent loads.
- **Groq (llama-3.3-70b)**: Chosen over other LLM providers specifically for inference speed. LPU technology allows for near-instant document processing, which is critical for real-time extraction tasks.
- **Dual-Path PDF Processing**: The system first attempts native text extraction using PyMuPDF. If the yield is insufficient (indicating a scanned document), it automatically routes through a high-resolution OCR pipeline using `pdf2image` and Tesseract.

## API Documentation

### POST /analyze

Upload a document for multi-dimensional analysis.

**Authentication**: `X-API-Key` header required.

**Supported Formats**:
- PDF (.pdf)
- Microsoft Word (.docx)
- Images (.png, .jpg, .jpeg, .tiff, .bmp, .webp)

**Example Request**:
```bash
curl -X POST "https://your-service-url.com/analyze" \
  -H "X-API-Key: your_service_api_key" \
  -F "file=@report.pdf"
```

**Example Response**:
```json
{
  "status": "success",
  "filename": "report.pdf",
  "file_type": "pdf",
  "extracted_text_preview": "Summary of Q3 financial performance...",
  "analysis": {
    "summary": "The report indicates a strong fiscal quarter with significant growth in the cloud sector...",
    "entities": [
      { "text": "Acme Corp", "type": "ORGANIZATION" },
      { "text": "$2.5M", "type": "MONEY" }
    ],
    "sentiment": {
      "label": "positive",
      "score": 0.85,
      "explanation": "Strong financial metrics and positive outlook statements."
    }
  },
  "metadata": {
    "processing_time_ms": 1240,
    "ocr_used": false,
    "page_count": 5,
    "word_count": 1250
  }
}
```

## Local Development

### Prerequisites
- Python 3.11+
- Tesseract OCR (Binary)
- Poppler (Binary for pdf2image)

### Setup
1.  **Clone the repository**:
    ```bash
    git clone https://github.com/shravipansare/doc-analysis-api.git
    cd doc-analysis-api
    ```
2.  **Environment Configuration**:
    Create a `.env` file based on `.env.example`:
    ```env
    GROQ_API_KEY=your_key
    SERVICE_API_KEY=your_random_string
    ```
3.  **Install dependencies**:
    ```bash
    pip install -r requirements.txt
    ```
4.  **Launch the server**:
    ```bash
    uvicorn app.main:app --host 0.0.0.0 --port 8000
    ```

## Roadmap

- [x] Support for multi-column layout analysis.
- [x] Table-to-Markdown extraction for complex financial reports.
- [x] Support for bulk document processing via batch endpoints.
- [x] Integration with vector databases for RAG-based document querying.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
