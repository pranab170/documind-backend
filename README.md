# DocuMind — CUTM RAG Document Assistant

Production-grade RAG system built on CUTM official documents.
Features hybrid BM25 + vector retrieval, RAGAS evaluation pipeline, and FastAPI backend.

---

## Project Structure

```
documind/
├── data/
│   ├── raw_docs/               ← CUTM .txt documents (already here)
│   ├── chroma_db/              ← Auto-created after ingestion
│   └── eval_results/           ← Auto-created after evaluation
├── src/
│   ├── ingestion/
│   │   └── ingest.py           ← Step 1: Load + Chunk + Embed docs
│   ├── retrieval/
│   │   ├── retriever.py        ← Step 2: Hybrid BM25 + Vector search + RRF
│   │   └── rag_chain.py        ← Step 3: LLM generation (Claude/OpenAI)
│   ├── api/
│   │   └── main.py             ← FastAPI server
│   └── eval/
│       └── evaluate.py         ← RAGAS evaluation pipeline
├── requirements.txt
├── .env.example
└── README.md
```

---

## Setup (Step by Step)

### 1. Create virtual environment
```bash
conda create -n documind python=3.11
conda activate documind
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Set up API keys
```bash
cp .env.example .env
# Edit .env and add your ANTHROPIC_API_KEY
```

### 4. Run ingestion (one-time setup)
This loads your CUTM docs, chunks them, embeds them, and stores in ChromaDB.
```bash
python -m src.ingestion.ingest
```
Expected output:
```
Loaded 3 documents
Created ~180 chunks
Vector store built with ~180 vectors
=== Ingestion Complete ===
```

### 5. Start the API server
```bash
uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000
```

### 6. Test a query
```bash
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{"query": "CUTM mein attendance kitni chahiye exam dene ke liye?"}'
```

### 7. Run evaluation
```bash
python -m src.eval.evaluate
```
Expected output:
```
Faithfulness      : 87.5%
Answer Relevancy  : 91.2%
Context Precision : 83.0%
Context Recall    : 79.8%
Overall Average   : 85.4%
```

---

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Health check + endpoint list |
| GET | `/health` | Retriever status + vector count |
| POST | `/query` | Main query endpoint |
| GET | `/debug/chunks?query=...` | See retrieved chunks + RRF scores |
| GET | `/docs` | Interactive Swagger UI |

### Query Request
```json
{
  "query": "What is the minimum attendance to appear in exams?",
  "top_k": 5
}
```

### Query Response
```json
{
  "query": "...",
  "answer": "According to the 2026 Examination Handbook, students must maintain...",
  "sources": ["CUTM_Examination_Handbook_2026_FULL.txt"],
  "source_chunks": [...],
  "model": "claude-sonnet-4-6",
  "context_chunks_used": 5,
  "latency_ms": 1240.5
}
```

---

## Resume Points (after building this)

- "Built a production RAG system with hybrid BM25 + semantic retrieval using Reciprocal Rank Fusion"
- "Implemented automated evaluation pipeline using RAGAS (faithfulness, answer relevancy, context precision, context recall)"
- "Achieved X% faithfulness score across 10 golden test queries on CUTM academic documents"
- "Deployed FastAPI backend with real-time observability (latency tracking, source citations)"

---

## Tech Stack

| Component | Technology |
|-----------|-----------|
| Embeddings | sentence-transformers/all-MiniLM-L6-v2 (free, local) |
| Vector DB | ChromaDB (local persistent) |
| Keyword Search | BM25Okapi (rank-bm25) |
| Ranking | Reciprocal Rank Fusion |
| LLM | Claude (claude-sonnet-4-6) |
| API | FastAPI + Uvicorn |
| Evaluation | RAGAS |
| Data | CUTM official documents (2026 Handbook + BTech Regulations) |
