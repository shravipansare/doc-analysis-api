import os
import uuid
import logging
from typing import List, Dict, Any

from sentence_transformers import SentenceTransformer
import chromadb

logger = logging.getLogger(__name__)

# Initialize singletons at module level
_chroma_client = None
_collection = None
_model = None

def _get_encoder():
    """Lazy load sentence transformer."""
    global _model
    if _model is None:
        logger.info("Loading sentence-transformers model...")
        _model = SentenceTransformer('all-MiniLM-L6-v2')
    return _model

def _get_collection():
    """Get or create ChromaDB client and collection."""
    global _chroma_client, _collection
    if _chroma_client is None:
        db_path = os.path.join(os.getcwd(), "chroma_data")
        logger.info(f"Initializing ChromaDB in {db_path}...")
        _chroma_client = chromadb.PersistentClient(path=db_path)
        
        # Use an embedding function bridge to SentenceTransformer
        class CustomEmbeddingFunction(chromadb.utils.embedding_functions.EmbeddingFunction):
            def __call__(self, input: chromadb.Documents) -> chromadb.Embeddings:
                model = _get_encoder()
                embeddings = model.encode(list(input))
                return embeddings.tolist()
                
        emb_fn = CustomEmbeddingFunction()
        _collection = _chroma_client.get_or_create_collection(
            name="document_collection",
            embedding_function=emb_fn
        )
    return _collection


def split_text_into_chunks(text: str, chunk_size: int = 1500, overlap: int = 200) -> List[str]:
    """Basic character-based window sliding chunker."""
    chunks = []
    start = 0
    while start < len(text):
        end = min(start + chunk_size, len(text))
        # Optional: could snap 'end' to a nearby newline
        snippet = text[start:end]
        chunks.append(snippet)
        if end >= len(text):
            break
        start = end - overlap
    return chunks

def index_document(text: str, filename: str) -> None:
    """Chunks the text and adds to the Chroma collection."""
    if not text.strip():
        return
        
    try:
        collection = _get_collection()
        chunks = split_text_into_chunks(text)
        
        if not chunks:
            return
            
        ids = [f"{filename}_{uuid.uuid4().hex[:8]}" for _ in chunks]
        metadatas = [{"filename": filename, "chunk_index": i} for i in range(len(chunks))]
        
        collection.add(
            documents=chunks,
            metadatas=metadatas,
            ids=ids
        )
        logger.info(f"Indexed {len(chunks)} chunks for database from {filename}.")
        
    except Exception as e:
        logger.error(f"Failed to index document {filename}: {e}")

def query_documents(query_text: str, top_k: int = 5) -> List[str]:
    """Retrieve top_k chunks matching the given query."""
    try:
        collection = _get_collection()
        results = collection.query(
            query_texts=[query_text],
            n_results=top_k
        )
        
        # results["documents"][0] gives list of matched chunk documents
        if results and "documents" in results and results["documents"]:
            return results["documents"][0]
        return []
    except Exception as e:
        logger.error(f"Failed to query ChromaDB: {e}")
        return []
