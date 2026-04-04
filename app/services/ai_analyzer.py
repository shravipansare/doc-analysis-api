import os
import json
import logging
import re
from typing import Any

from groq import Groq

from app.models.schemas import Analysis, Entity, Sentiment

logger = logging.getLogger(__name__)

# Initialize Groq client (reads GROQ_API_KEY from environment)
_client: Groq | None = None


def get_client() -> Groq:
    global _client
    if _client is None:
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise RuntimeError("GROQ_API_KEY environment variable is not set.")
        _client = Groq(api_key=api_key)
    return _client


ANALYSIS_PROMPT = """You are an expert document analysis AI. Analyze the following document text and return a JSON response with EXACTLY this structure (no extra keys, no markdown fences):

{{
  "summary": "<A concise 2-4 sentence summary of the document's main content and purpose>",
  "entities": [
    {{"text": "<entity text>", "type": "<PERSON|ORGANIZATION|LOCATION|DATE|MONEY|PRODUCT|EVENT|OTHER>"}}
  ],
  "sentiment": {{
    "label": "<positive|negative|neutral>",
    "score": <float between -1.0 (most negative) and 1.0 (most positive)>,
    "explanation": "<One sentence explaining why this sentiment classification was chosen>"
  }}
}}

Rules:
- Extract ALL significant named entities: people names, organization names, locations, dates, monetary amounts, products, events.
- If no entities exist, return an empty array [].
- Sentiment score: 1.0 = very positive, 0.0 = neutral, -1.0 = very negative.
- Keep the summary factual and informative.
- Return ONLY valid JSON. No markdown code blocks. No extra text before or after.

Document Text:
---
{text}
---"""


def analyze_text(text: str) -> Analysis:
    """
    Send extracted text to Groq (llama-3.3-70b-versatile) for AI analysis.

    Returns an Analysis object with summary, entities, and sentiment.
    """
    client = get_client()

    # Truncate text to ~12,000 tokens worth (~48,000 chars) to stay within limits
    truncated_text = text[:48000] if len(text) > 48000 else text

    prompt = ANALYSIS_PROMPT.format(text=truncated_text)

    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {
                    "role": "system",
                    "content": "You are a precise document analysis AI that always responds with valid JSON only.",
                },
                {"role": "user", "content": prompt},
            ],
            temperature=0.1,  # Low temperature for consistent, factual output
            max_tokens=2048,
            response_format={"type": "json_object"},
        )

        raw_content = response.choices[0].message.content.strip()
        logger.debug(f"Groq raw response: {raw_content[:500]}")

        return _parse_analysis(raw_content)

    except Exception as e:
        logger.error(f"Groq API call failed: {e}")
        raise


def _parse_analysis(raw_json: str) -> Analysis:
    """Parse and validate the Groq JSON response into an Analysis object."""
    try:
        # Remove markdown fences if present (defensive)
        clean = re.sub(r"```(?:json)?\s*|\s*```", "", raw_json).strip()
        data: dict[str, Any] = json.loads(clean)

        # Parse entities
        entities = []
        for ent in data.get("entities", []):
            if isinstance(ent, dict) and "text" in ent and "type" in ent:
                entities.append(
                    Entity(
                        text=str(ent["text"]).strip(),
                        type=str(ent["type"]).upper().strip(),
                    )
                )

        # Parse sentiment
        sentiment_data = data.get("sentiment", {})
        sentiment = Sentiment(
            label=str(sentiment_data.get("label", "neutral")).lower().strip(),
            score=float(sentiment_data.get("score", 0.0)),
            explanation=str(
                sentiment_data.get("explanation", "No explanation provided.")
            ).strip(),
        )

        # Clamp score to [-1.0, 1.0]
        sentiment.score = max(-1.0, min(1.0, sentiment.score))

        summary = str(data.get("summary", "No summary available.")).strip()

        return Analysis(summary=summary, entities=entities, sentiment=sentiment)

    except (json.JSONDecodeError, KeyError, TypeError, ValueError) as e:
        logger.error(f"Failed to parse Groq response: {e}. Raw: {raw_json[:300]}")
        # Return a safe fallback instead of crashing
        return Analysis(
            summary="Unable to generate summary due to a parsing error.",
            entities=[],
            sentiment=Sentiment(
                label="neutral",
                score=0.0,
                explanation="Sentiment analysis failed due to a parsing error.",
            ),
        )

RAG_PROMPT = """You are a helpful and intelligent question answering assistant. 
Use the following retrieved context to answer the user's question. 
If the answer cannot be found in the context, simply say "I'm sorry, I cannot find the answer to this question in the provided documents." 
Do NOT make up information.

Context:
---
{context}
---

Question: {question}

Answer:"""

def generate_rag_response(context_chunks: list[str], query: str) -> str:
    """Generate an answer using Groq and the provided chunks."""
    if not context_chunks:
        return "I'm sorry, I don't have enough context from the documents to answer that."

    client = get_client()
    merged_context = "\n\n".join(context_chunks)
    prompt = RAG_PROMPT.format(context=merged_context, question=query)

    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": "You are a precise QA assistant."},
                {"role": "user", "content": prompt},
            ],
            temperature=0.2,
            max_tokens=1024,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        logger.error(f"RAG Groq generation failed: {e}")
        return "Sorry, I encountered an error while trying to answer your question."
