"""
DocuMind - FastAPI Backend
Serves the RAG pipeline via REST API.
Run with: uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000
"""

import time
import logging
from typing import List, Optional
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from retriever import get_retriever
from rag_chain import generate_answer

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="DocuMind API",
    description="RAG-based CUTM Document Intelligence Assistant",
    version="1.0.0",
)

# Yeh code Vercel/Netlify/Cloudflare (Frontend) ko Render (Backend) se baat karne dega
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Security ke liye baad mein isko apne frontend URL se replace kar sakte hain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Request / Response Models ─────────────────────────────────────────────────

class QueryRequest(BaseModel):
    query: str
    top_k: Optional[int] = 5

class SourceChunk(BaseModel):
    content: str
    filename: str
    doc_type: str
    chunk_id: int

class QueryResponse(BaseModel):
    query: str
    answer: str
    sources: List[str]
    source_chunks: List[SourceChunk]
    model: str
    context_chunks_used: int
    latency_ms: float


# ── Routes ────────────────────────────────────────────────────────────────────

@app.get("/")
def root():
    return {
        "status": "ok",
        "app": "DocuMind",
        "description": "CUTM Document Intelligence Assistant",
        "endpoints": ["/query", "/health", "/docs"],
    }


@app.get("/health")
def health():
    try:
        retriever = get_retriever()
        doc_count = retriever._vectorstore._collection.count()
        return {
            "status": "healthy",
            "vector_store_docs": doc_count,
        }
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Retriever not ready: {str(e)}")


@app.post("/query", response_model=QueryResponse)
def query(request: QueryRequest):
    """
    Main query endpoint.
    Takes a student question, retrieves relevant CUTM doc chunks,
    and returns a grounded answer with citations.
    """
    if not request.query.strip():
        raise HTTPException(status_code=400, detail="Query cannot be empty")

    start = time.time()

    try:
        # Step 1: Hybrid retrieval
        retriever = get_retriever()
        retriever.top_k = request.top_k or 5
        docs = retriever.retrieve(request.query)

        # Step 2: Generate answer
        result = generate_answer(request.query, docs)

        # Step 3: Build source chunk details
        source_chunks = [
            SourceChunk(
                content=doc.page_content,
                filename=doc.metadata.get("filename", "unknown"),
                doc_type=doc.metadata.get("doc_type", "general"),
                chunk_id=doc.metadata.get("chunk_id", -1),
            )
            for doc in docs
        ]

        latency = (time.time() - start) * 1000
        logger.info(f"Query answered in {latency:.0f}ms | model: {result['model']}")

        return QueryResponse(
            query=request.query,
            answer=result["answer"],
            sources=result["sources"],
            source_chunks=source_chunks,
            model=result["model"],
            context_chunks_used=result["context_chunks_used"],
            latency_ms=round(latency, 2),
        )

    except Exception as e:
        logger.error(f"Query error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/debug/chunks")
def debug_chunks(query: str, top_k: int = 5):
    """
    Debug endpoint: shows retrieved chunks with their RRF scores.
    Useful during development to tune retrieval quality.
    """
    try:
        retriever = get_retriever()
        retriever.top_k = top_k
        results = retriever.retrieve_with_scores(query)
        return {
            "query": query,
            "chunks": [
                {
                    "rank": i + 1,
                    "rrf_score": round(score, 6),
                    "filename": doc.metadata.get("filename", "unknown"),
                    "chunk_id": doc.metadata.get("chunk_id", -1),
                    "content_preview": doc.page_content[:200] + "...",
                }
                for i, (doc, score) in enumerate(results)
            ],
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))