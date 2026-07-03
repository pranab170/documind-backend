"""
DocuMind - Hybrid Retrieval Module
Combines BM25 (keyword) + Vector (semantic) search using Reciprocal Rank Fusion.
This is the KEY differentiator that makes DocuMind better than basic RAG.
"""

import os
import logging
from typing import List, Tuple
from dotenv import load_dotenv

from rank_bm25 import BM25Okapi
from langchain.schema import Document
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_chroma import Chroma

load_dotenv()
logger = logging.getLogger(__name__)

CHROMA_DB_PATH = os.getenv("CHROMA_DB_PATH", "./data/chroma_db")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2")


class HybridRetriever:
    """
    Retrieves relevant chunks using:
    1. BM25 (keyword exact match) - great for specific rule numbers, percentages
    2. Vector similarity (semantic) - great for meaning-based queries
    3. Reciprocal Rank Fusion (RRF) - combines both rankings optimally
    """

    def __init__(self, top_k: int = 5, rrf_k: int = 60):
        self.top_k = top_k
        self.rrf_k = rrf_k  # RRF constant (60 is standard)
        self._embeddings = None
        self._vectorstore = None
        self._bm25 = None
        self._all_chunks = []

    def _load_embeddings(self):
        if self._embeddings is None:
            logger.info("Loading embedding model...")
            self._embeddings = HuggingFaceEmbeddings(
                model_name=EMBEDDING_MODEL,
                model_kwargs={"device": "cpu"},
                encode_kwargs={"normalize_embeddings": True},
            )
        return self._embeddings

    def load_vectorstore(self):
        """Load existing ChromaDB vector store."""
        embeddings = self._load_embeddings()
        self._vectorstore = Chroma(
            persist_directory=CHROMA_DB_PATH,
            embedding_function=embeddings,
            collection_name="cutm_docs",
        )
        # Load all chunks into memory for BM25 (works fine for small corpora like CUTM docs)
        self._all_chunks = self._vectorstore.get()
        self._build_bm25()
        logger.info(f"Loaded {len(self._all_chunks['documents'])} chunks into retriever")

    def _build_bm25(self):
        """Build BM25 index from all stored documents."""
        tokenized = [doc.lower().split() for doc in self._all_chunks["documents"]]
        self._bm25 = BM25Okapi(tokenized)
        logger.info("BM25 index built")

    def _vector_search(self, query: str, top_n: int) -> List[Tuple[Document, float]]:
        """Pure vector similarity search."""
        results = self._vectorstore.similarity_search_with_score(query, k=top_n * 2)
        # Chroma returns (doc, distance) — lower distance = more similar
        # Normalize to similarity score (1 - normalized_distance)
        return results

    def _bm25_search(self, query: str, top_n: int) -> List[Tuple[int, float]]:
        """BM25 keyword search, returns (chunk_index, score) pairs."""
        tokens = query.lower().split()
        scores = self._bm25.get_scores(tokens)
        # Get indices sorted by BM25 score (descending)
        ranked = sorted(enumerate(scores), key=lambda x: x[1], reverse=True)
        return ranked[:top_n * 2]

    def _reciprocal_rank_fusion(
        self,
        vector_results: List[Tuple[Document, float]],
        bm25_results: List[Tuple[int, float]],
    ) -> List[Document]:
        """
        RRF formula: score(d) = sum(1 / (k + rank_i)) for each ranking i
        Higher RRF score = more relevant document.
        """
        rrf_scores = {}

        # Score vector results (rank-based, not score-based)
        for rank, (doc, _score) in enumerate(vector_results):
            doc_key = doc.page_content[:100]  # use content snippet as unique key
            rrf_scores[doc_key] = rrf_scores.get(doc_key, {"doc": doc, "score": 0})
            rrf_scores[doc_key]["score"] += 1.0 / (self.rrf_k + rank + 1)

        # Score BM25 results
        all_docs = self._all_chunks["documents"]
        all_metas = self._all_chunks["metadatas"]
        for rank, (idx, _score) in enumerate(bm25_results):
            if idx >= len(all_docs):
                continue
            content = all_docs[idx]
            doc_key = content[:100]
            if doc_key not in rrf_scores:
                doc_obj = Document(page_content=content, metadata=all_metas[idx] or {})
                rrf_scores[doc_key] = {"doc": doc_obj, "score": 0}
            rrf_scores[doc_key]["score"] += 1.0 / (self.rrf_k + rank + 1)

        # Sort by combined RRF score
        ranked = sorted(rrf_scores.values(), key=lambda x: x["score"], reverse=True)
        return [item["doc"] for item in ranked[: self.top_k]]

    def retrieve(self, query: str) -> List[Document]:
        """
        Main retrieval method. Returns top_k most relevant chunks for a query.
        Uses hybrid BM25 + vector search with RRF fusion.
        """
        if self._vectorstore is None:
            raise RuntimeError("Call load_vectorstore() before retrieve()")

        logger.info(f"Hybrid retrieval for query: '{query[:60]}...'")

        # Run both searches
        vector_results = self._vector_search(query, self.top_k)
        bm25_results = self._bm25_search(query, self.top_k)

        # Fuse rankings
        final_docs = self._reciprocal_rank_fusion(vector_results, bm25_results)

        logger.info(f"Retrieved {len(final_docs)} chunks after RRF fusion")
        return final_docs

    def retrieve_with_scores(self, query: str) -> List[Tuple[Document, float]]:
        """Returns chunks with their RRF scores (useful for debugging/eval)."""
        if self._vectorstore is None:
            raise RuntimeError("Call load_vectorstore() before retrieve()")

        vector_results = self._vector_search(query, self.top_k)
        bm25_results = self._bm25_search(query, self.top_k)

        rrf_scores = {}
        all_docs = self._all_chunks["documents"]
        all_metas = self._all_chunks["metadatas"]

        for rank, (doc, _) in enumerate(vector_results):
            doc_key = doc.page_content[:100]
            rrf_scores[doc_key] = rrf_scores.get(doc_key, {"doc": doc, "score": 0})
            rrf_scores[doc_key]["score"] += 1.0 / (self.rrf_k + rank + 1)

        for rank, (idx, _) in enumerate(bm25_results):
            if idx >= len(all_docs):
                continue
            content = all_docs[idx]
            doc_key = content[:100]
            if doc_key not in rrf_scores:
                doc_obj = Document(page_content=content, metadata=all_metas[idx] or {})
                rrf_scores[doc_key] = {"doc": doc_obj, "score": 0}
            rrf_scores[doc_key]["score"] += 1.0 / (self.rrf_k + rank + 1)

        ranked = sorted(rrf_scores.values(), key=lambda x: x["score"], reverse=True)
        return [(item["doc"], item["score"]) for item in ranked[: self.top_k]]


# Singleton instance for use across the app
_retriever_instance = None


def get_retriever() -> HybridRetriever:
    global _retriever_instance
    if _retriever_instance is None:
        _retriever_instance = HybridRetriever(top_k=5)
        _retriever_instance.load_vectorstore()
    return _retriever_instance
