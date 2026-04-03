# 🧠 AI-Powered Document Analysis API

[![Live Demo](https://img.shields.io/badge/Live-API-green)](https://your-app.onrender.com)
[![Python](https://img.shields.io/badge/Python-3.11-blue)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688)](https://fastapi.tiangolo.com)
[![Model](https://img.shields.io/badge/Model-llama--3.3--70b-orange)](https://console.groq.com)

An intelligent document processing API that extracts, analyses, and summarises content from **PDF**, **DOCX**, and **image** files using OCR and AI.

## ✨ Features

| Feature | Technology |
|---------|-----------|
| PDF text extraction | PyMuPDF (native) + Tesseract OCR (scanned) |
| DOCX text extraction | python-docx (paragraphs + tables) |
| Image OCR | Tesseract + Pillow preprocessing |
| AI Summarisation | Groq `llama-3.3-70b-versatile` |
| Entity Extraction | Persons, Org, Location, Date, Money |
| Sentiment Analysis | Positive / Negative / Neutral (-1.0 to 1.0) |
| API Framework | FastAPI + Uvicorn (async) |
| Deployment | Render.com |

---

## 📡 API Documentation

**Base URL**: `https://your-app.onrender.com`  
**Authentication**: `X-API-Key` header

### `POST /analyze`

Upload a document for analysis.

**Request** (`multipart/form-data`):

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `file` | File | ✅ | PDF, DOCX, PNG, JPG, JPEG, TIFF, BMP, WEBP |

**Headers**:
```
X-API-Key: <your-api-key>
```

**Response** (`200 OK`):
```json
{
  "status": "success",
  "filename": "report.pdf",
  "file_type": "pdf",
  "extracted_text_preview": "First 500 characters of extracted text...",
  "analysis": {
    "summary": "Concise 2-4 sentence summary of the document.",
    "entities": [
      { "text": "John Smith", "type": "PERSON" },
      { "text": "Acme Corporation", "type": "ORGANIZATION" },
      { "text": "New York", "type": "LOCATION" },
      { "text": "January 15, 2024", "type": "DATE" },
      { "text": "$50,000", "type": "MONEY" }
    ],
    "sentiment": {
      "label": "positive",
      "score": 0.72,
      "explanation": "The document presents optimistic financial results and future projections."
    }
  },
  "metadata": {
    "processing_time_ms": 1840,
    "ocr_used": false,
    "page_count": 3,
    "word_count": 1250
  }
}
```

**Error Responses**:
```json
{ "status": "error", "error_code": "UNSUPPORTED_FORMAT", "message": "..." }
{ "status": "error", "error_code": "EMPTY_FILE", "message": "..." }
{ "status": "error", "error_code": "NO_TEXT_EXTRACTED", "message": "..." }
{ "status": "error", "error_code": "UNAUTHORIZED", "message": "..." }
```

---

### `GET /health`

Health check endpoint.

```json
{ "status": "ok", "version": "1.0.0", "model": "llama-3.3-70b-versatile" }
```

---

## 🚀 Quick Start (Local)

### Prerequisites
- Python 3.11+
- [Tesseract OCR](https://github.com/tesseract-ocr/tesseract) installed
- [Poppler](https://poppler.freedesktop.org/) installed (for PDF→image conversion)

### Installation

```bash
# Clone the repository
git clone https://github.com/your-username/doc-analysis-api.git
cd doc-analysis-api

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env and add your GROQ_API_KEY and SERVICE_API_KEY
```

### Running Locally

```bash
uvicorn app.main:app --reload --port 8000
```

Visit: http://localhost:8000

### Test with curl

**PDF:**
```bash
curl -X POST "http://localhost:8000/analyze" \
  -H "X-API-Key: your-service-api-key" \
  -F "file=@sample.pdf"
```

**DOCX:**
```bash
curl -X POST "http://localhost:8000/analyze" \
  -H "X-API-Key: your-service-api-key" \
  -F "file=@document.docx"
```

**Image:**
```bash
curl -X POST "http://localhost:8000/analyze" \
  -H "X-API-Key: your-service-api-key" \
  -F "file=@image.png"
```

---

## 🐳 Docker Deployment

```bash
# Build image
docker build -t doc-analysis-api .

# Run container
docker run -p 8000:8000 \
  -e GROQ_API_KEY=your_key \
  -e SERVICE_API_KEY=your_service_key \
  doc-analysis-api
```

---

## ☁️ Deploy to Render

1. Push repo to GitHub
2. Go to [render.com](https://render.com) → New Web Service
3. Connect your GitHub repo
4. Render will auto-detect `render.yaml`
5. Set `GROQ_API_KEY` and `SERVICE_API_KEY` in Render dashboard → Environment
6. Deploy!

---

## 🏗️ Architecture

```
POST /analyze
    │
    ├── File Type Detection (.pdf, .docx, .png, ...)
    │
    ├── Text Extraction
    │     ├── PDF → PyMuPDF → OCR fallback (pdf2image + Tesseract)
    │     ├── DOCX → python-docx
    │     └── Image → Pillow preprocessing → Tesseract
    │
    └── AI Analysis (Groq llama-3.3-70b-versatile)
          ├── Summary
          ├── Named Entity Extraction
          └── Sentiment Analysis
```

---

## 📁 Project Structure

```
doc-analysis-api/
├── app/
│   ├── main.py              # FastAPI app, CORS, health, landing page
│   ├── routers/
│   │   └── analyze.py       # POST /analyze endpoint
│   ├── services/
│   │   ├── extractor.py     # PDF/DOCX/Image text extraction
│   │   └── ai_analyzer.py   # Groq API (summary + entities + sentiment)
│   ├── models/
│   │   └── schemas.py       # Pydantic models
│   └── utils/
│       └── file_utils.py    # File type detection
├── requirements.txt
├── Dockerfile
├── render.yaml
├── .env.example
└── README.md
```

---

## 🔐 Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `GROQ_API_KEY` | ✅ | Groq API key from console.groq.com |
| `SERVICE_API_KEY` | ⚠️ | API key for authenticating requests. Leave empty to disable auth (dev only). |

---

## 📄 License

MIT License — feel free to use and modify.
