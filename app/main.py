import os
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
from dotenv import load_dotenv

from app.routers import analyze

# Load environment variables from .env file (for local development)
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup/shutdown lifecycle handler."""
    logger.info("🚀 Document Analysis API starting up...")
    # Pre-warm Groq client
    groq_key = os.getenv("GROQ_API_KEY", "")
    if not groq_key:
        logger.warning("⚠️  GROQ_API_KEY not set — AI analysis will fail!")
    else:
        logger.info("✅ Groq API key loaded.")
    yield
    logger.info("🛑 Document Analysis API shutting down.")


# --------------------------------------------------------------------------- #
# App setup
# --------------------------------------------------------------------------- #
app = FastAPI(
    title="AI-Powered Document Analysis API",
    description=(
        "Extract text from PDF, DOCX, and image files. "
        "Powered by Tesseract OCR and Groq (llama-3.3-70b-versatile) for "
        "summarization, entity extraction, and sentiment analysis."
    ),
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS — allow all origins (required for evaluator access)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(analyze.router, tags=["Document Analysis"])


# --------------------------------------------------------------------------- #
# Health check
# --------------------------------------------------------------------------- #
@app.get("/health", summary="Health check", tags=["System"])
async def health_check():
    return {"status": "ok", "version": "1.0.0", "model": "llama-3.3-70b-versatile"}


# --------------------------------------------------------------------------- #
# Root — HTML landing page
# --------------------------------------------------------------------------- #
@app.get("/", response_class=HTMLResponse, summary="API Documentation landing page", tags=["System"])
async def root():
    return HTMLResponse(content="""
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8"/>
  <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
  <title>AI Document Analysis API</title>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap" rel="stylesheet"/>
  <style>
    *{margin:0;padding:0;box-sizing:border-box}
    body{font-family:'Inter',sans-serif;background:#0a0a0f;color:#e2e8f0;min-height:100vh;display:flex;align-items:center;justify-content:center;padding:2rem}
    .container{max-width:800px;width:100%}
    h1{font-size:2.5rem;font-weight:700;background:linear-gradient(135deg,#6366f1,#8b5cf6,#a78bfa);-webkit-background-clip:text;-webkit-text-fill-color:transparent;margin-bottom:0.5rem}
    .subtitle{color:#94a3b8;font-size:1.1rem;margin-bottom:2.5rem}
    .card{background:rgba(255,255,255,0.05);border:1px solid rgba(255,255,255,0.1);border-radius:16px;padding:1.5rem;margin-bottom:1.5rem;backdrop-filter:blur(10px)}
    .card h2{font-size:1.1rem;font-weight:600;color:#a78bfa;margin-bottom:1rem}
    .endpoint{display:flex;align-items:center;gap:0.75rem;margin-bottom:0.75rem}
    .method{background:#6366f1;color:white;padding:0.25rem 0.6rem;border-radius:6px;font-size:0.8rem;font-weight:600;min-width:60px;text-align:center}
    .method.get{background:#10b981}
    .path{font-family:monospace;color:#e2e8f0;font-size:0.95rem}
    .desc{color:#94a3b8;font-size:0.85rem;margin-left:auto}
    .features{display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:1rem}
    .feature{background:rgba(99,102,241,0.1);border:1px solid rgba(99,102,241,0.2);border-radius:12px;padding:1rem;text-align:center}
    .feature .icon{font-size:1.8rem;margin-bottom:0.5rem}
    .feature h3{font-size:0.9rem;font-weight:600;color:#a78bfa}
    .feature p{font-size:0.8rem;color:#94a3b8;margin-top:0.25rem}
    .btn{display:inline-block;background:linear-gradient(135deg,#6366f1,#8b5cf6);color:white;padding:0.75rem 1.5rem;border-radius:10px;text-decoration:none;font-weight:600;margin-top:0.5rem;transition:opacity 0.2s}
    .btn:hover{opacity:0.85}
    code{background:rgba(255,255,255,0.1);padding:0.2rem 0.4rem;border-radius:4px;font-size:0.85rem;font-family:monospace}
    .badge{display:inline-block;background:rgba(16,185,129,0.2);color:#10b981;border:1px solid rgba(16,185,129,0.3);padding:0.2rem 0.6rem;border-radius:20px;font-size:0.75rem;font-weight:600;margin-left:0.5rem}
  </style>
</head>
<body>
  <div class="container">
    <h1>🧠 AI Document Analysis API</h1>
    <p class="subtitle">Intelligent extraction &amp; analysis for PDF, DOCX, and image files <span class="badge">v1.0.0 LIVE</span></p>

    <div class="features">
      <div class="feature">
        <div class="icon">📄</div>
        <h3>Multi-Format Support</h3>
        <p>PDF, DOCX, PNG, JPG, TIFF, BMP, WEBP</p>
      </div>
      <div class="feature">
        <div class="icon">🔍</div>
        <h3>OCR Extraction</h3>
        <p>Tesseract OCR with image preprocessing</p>
      </div>
      <div class="feature">
        <div class="icon">✨</div>
        <h3>AI Summarisation</h3>
        <p>Powered by Groq llama-3.3-70b</p>
      </div>
      <div class="feature">
        <div class="icon">🏷️</div>
        <h3>Entity Extraction</h3>
        <p>People, Orgs, Locations, Dates, Money</p>
      </div>
      <div class="feature">
        <div class="icon">💬</div>
        <h3>Sentiment Analysis</h3>
        <p>Positive / Negative / Neutral + score</p>
      </div>
      <div class="feature">
        <div class="icon">⚡</div>
        <h3>Fast Processing</h3>
        <p>Async API with millisecond response</p>
      </div>
    </div>

    <div class="card" style="margin-top:1.5rem">
      <h2>📡 Endpoints</h2>
      <div class="endpoint">
        <span class="method">POST</span>
        <span class="path">/analyze</span>
        <span class="desc">Upload &amp; analyse a document</span>
      </div>
      <div class="endpoint">
        <span class="method get">GET</span>
        <span class="path">/health</span>
        <span class="desc">Health check</span>
      </div>
      <div class="endpoint">
        <span class="method get">GET</span>
        <span class="path">/docs</span>
        <span class="desc">Swagger UI</span>
      </div>
    </div>

    <div class="card">
      <h2>🚀 Quick Start</h2>
      <p style="color:#94a3b8;font-size:0.9rem;margin-bottom:0.75rem">Send a file via multipart form with your API key in the <code>X-API-Key</code> header:</p>
      <code style="display:block;padding:1rem;background:rgba(0,0,0,0.4);border-radius:8px;font-size:0.82rem;line-height:1.6;white-space:pre-wrap">curl -X POST "https://your-app.onrender.com/analyze" \\
  -H "X-API-Key: your-api-key" \\
  -F "file=@document.pdf"</code>
      <br/>
      <a href="/docs" class="btn">Open Swagger UI →</a>
    </div>
  </div>
</body>
</html>
""")


# --------------------------------------------------------------------------- #
# Global exception handler
# --------------------------------------------------------------------------- #
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.exception(f"Unhandled exception on {request.url}: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "status": "error",
            "error_code": "INTERNAL_SERVER_ERROR",
            "message": "An unexpected internal error occurred.",
        },
    )
