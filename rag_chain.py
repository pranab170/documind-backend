import os
import logging
import requests
from typing import List, Dict, Any
from langchain.schema import Document

logger = logging.getLogger(__name__)
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

SYSTEM_PROMPT = """You are DocuMind, an assistant for CUTM students.
Answer questions about CUTM academic regulations and exam rules.
ONLY answer based on the provided context. If not in context, say
"I couldn't find this in CUTM documents. Please check with your exam cell."
Always cite the source document. Be precise with numbers and percentages
NEVER make up numbers, calculations, or facts not explicitly stated in the context.
If exact answer is in context, quote it directly word for word.
Do NOT perform any math or calculations on your own."""

def _build_context(docs: List[Document]) -> str:
    parts = []
    for i, doc in enumerate(docs, 1):
        filename = doc.metadata.get("filename", "CUTM Document")
        parts.append(f"[Source {i}: {filename}]\n{doc.page_content}")
    return "\n\n---\n\n".join(parts)

def generate_answer(query: str, docs: List[Document]) -> Dict[str, Any]:
    if not docs:
        return {
            "answer": "No relevant documents found.",
            "sources": [],
            "model": "none",
            "context_chunks_used": 0,
        }

    context = _build_context(docs)

    response = requests.post(
        "https://api.groq.com/openai/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {GROQ_API_KEY}",
            "Content-Type": "application/json",
        },
        json={
            "model": "llama-3.1-8b-instant",
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": f"Context:\n{context}\n\nQuestion: {query}"},
            ],
            "max_tokens": 1024,
            "temperature": 0,
        },
        timeout=30,
    )
    response.raise_for_status()
    answer = response.json()["choices"][0]["message"]["content"]
    sources = list({doc.metadata.get("filename", "CUTM Document") for doc in docs})

    return {
        "answer": answer,
        "sources": sources,
        "model": "llama-3.1-8b-instant (Groq)",
        "context_chunks_used": len(docs),
    }