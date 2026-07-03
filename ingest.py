"""
DocuMind - Document Ingestion Pipeline
Loads CUTM .txt documents, chunks them intelligently, embeds and stores in ChromaDB.
"""

import os
import re
import logging
from pathlib import Path
from typing import List, Dict
from dotenv import load_dotenv

from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import TextLoader, DirectoryLoader
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain.schema import Document

load_dotenv()
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

RAW_DOCS_PATH = os.getenv("RAW_DOCS_PATH", "./data/raw_docs")
CHROMA_DB_PATH = os.getenv("CHROMA_DB_PATH", "./data/chroma_db")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2")


def load_documents(docs_path: str) -> List[Document]:
    """Load all .txt files from the raw_docs folder."""
    logger.info(f"Loading documents from: {docs_path}")

    loader = DirectoryLoader(
        docs_path,
        glob="**/*.txt",
        loader_cls=TextLoader,
        loader_kwargs={"encoding": "utf-8"},
        show_progress=True,
    )
    docs = loader.load()

    # Attach clean metadata to each doc
    for doc in docs:
        filename = Path(doc.metadata["source"]).name
        doc.metadata["filename"] = filename
        doc.metadata["doc_type"] = _classify_doc(filename)

    logger.info(f"Loaded {len(docs)} documents")
    return docs


def _classify_doc(filename: str) -> str:
    """Tag each document with a type for metadata filtering later."""
    if "BTech" in filename or "CBCS" in filename:
        return "btech_regulations"
    elif "Handbook" in filename or "Examination" in filename:
        return "exam_handbook"
    return "general"


def chunk_documents(docs: List[Document]) -> List[Document]:
    """
    Split documents into overlapping chunks.
    Strategy: recursive splitting that respects section boundaries.
    Chunk size 800 tokens, 150 overlap — good balance for exam rule queries.
    """
    logger.info("Chunking documents...")

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=800,
        chunk_overlap=150,
        length_function=len,
        separators=[
            "\n================================================================\n",
            "\nAnnexure",
            "\n\n",
            "\n",
            ". ",
            " ",
        ],
    )

    chunks = splitter.split_documents(docs)

    # Add chunk index metadata for debugging
    for i, chunk in enumerate(chunks):
        chunk.metadata["chunk_id"] = i
        chunk.metadata["chunk_size"] = len(chunk.page_content)

    logger.info(f"Created {len(chunks)} chunks from {len(docs)} documents")
    _log_chunk_stats(chunks)
    return chunks


def _log_chunk_stats(chunks: List[Document]):
    sizes = [len(c.page_content) for c in chunks]
    logger.info(f"Chunk stats → min: {min(sizes)}, max: {max(sizes)}, avg: {sum(sizes)//len(sizes)}")


def build_vectorstore(chunks: List[Document]) -> Chroma:
    """Embed chunks using local HuggingFace model and store in ChromaDB."""
    logger.info(f"Loading embedding model: {EMBEDDING_MODEL}")

    embeddings = HuggingFaceEmbeddings(
        model_name=EMBEDDING_MODEL,
        model_kwargs={"device": "cpu"},
        encode_kwargs={"normalize_embeddings": True},
    )

    logger.info(f"Building ChromaDB vector store at: {CHROMA_DB_PATH}")
    os.makedirs(CHROMA_DB_PATH, exist_ok=True)

    vectorstore = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory=CHROMA_DB_PATH,
        collection_name="cutm_docs",
    )

    logger.info(f"Vector store built with {vectorstore._collection.count()} vectors")
    return vectorstore


def run_ingestion():
    """Full ingestion pipeline: load → chunk → embed → store."""
    logger.info("=== DocuMind Ingestion Pipeline Started ===")

    # Step 1: Load
    docs = load_documents(RAW_DOCS_PATH)
    if not docs:
        logger.error(f"No documents found in {RAW_DOCS_PATH}. Add your .txt files there.")
        return

    # Step 2: Chunk
    chunks = chunk_documents(docs)

    # Step 3: Embed + Store
    vectorstore = build_vectorstore(chunks)

    logger.info("=== Ingestion Complete ===")
    logger.info(f"Total vectors stored: {vectorstore._collection.count()}")
    return vectorstore


if __name__ == "__main__":
    run_ingestion()
