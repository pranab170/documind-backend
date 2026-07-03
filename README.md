# 🧠 DocuMind - CUTM Document Intelligence Assistant

> An interactive, AI-powered RAG (Retrieval-Augmented Generation) assistant designed to instantly navigate, retrieve, and answer queries regarding the official academic regulations and handbooks of Centurion University of Technology and Management (CUTM).

![DocuMind Demo](https://img.shields.io/badge/Status-Live-success?style=for-the-badge)
![Python](https://img.shields.io/badge/Python-3.11-blue?style=for-the-badge&logo=python)
![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi)
![React](https://img.shields.io/badge/React-20232A?style=for-the-badge&logo=react&logoColor=61DAFB)
![Hugging Face](https://img.shields.io/badge/Hugging%20Face-Spaces-F58025?style=for-the-badge&logo=huggingface)

---

## ✨ Key Features

* **Hybrid Retrieval System:** Combines traditional keyword search (BM25) with semantic vector search (ChromaDB) for highly accurate document retrieval.
* **Reciprocal Rank Fusion (RRF):** Intelligently merges results from both retrieval methods to surface the most relevant context chunks.
* **Source Citations:** Generates grounded answers and provides exact source chunks (document names and text snippets) used to formulate the response.
* **Optimized LLM Inference:** Powered by Groq API for lightning-fast response generation.
* **Modern UI/UX:** A sleek, dark-mode React frontend for a seamless interactive chat experience.

---

## 🛠️ Tech Stack

**Frontend:**
* React (Vite)
* Tailwind CSS (Styling)
* Hosted on **Cloudflare Pages**

**Backend:**
* FastAPI (REST API framework)
* LangChain (Orchestration)
* ChromaDB (Vector Database)
* HuggingFace `sentence-transformers/all-MiniLM-L6-v2` (Embeddings)
* Groq API (LLM for text generation)
* Containerized with Docker & Hosted on **Hugging Face Spaces** (16GB RAM, 2vCPU)

---

## 🏗️ System Architecture

1. **Ingestion:** CUTM rulebooks (PDFs/TXTs) are chunked and embedded using HuggingFace models, then stored locally in ChromaDB.
2. **Retrieval:** User queries trigger a parallel search—BM25 looks for exact rule numbers/keywords, while ChromaDB finds semantic meaning.
3. **Fusion:** RRF algorithms rank the best chunks from both pipelines.
4. **Generation:** The top chunks are sent to the Groq LLM along with the user's query to synthesize a factual, referenced answer.

---

## 🚀 Local Setup & Installation

### Prerequisites
* Python 3.11+
* Node.js & npm

### Backend Setup
1. Clone the repository:
   ```bash
   git clone [https://github.com/pranab170/documind-backend.git](https://github.com/pranab170/documind-backend.git)
   cd documind-backend

   Install Python dependencies:

Bash
pip install -r requirements.txt
Set up Environment Variables:
Create a .env file in the root directory and add your Groq API key:

Code snippet
GROQ_API_KEY=gsk_your_api_key_here
Start the FastAPI Server:

Bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
The API will be available at http://localhost:8000

Frontend Setup
Navigate to the frontend directory:

Bash
cd documind-frontend
Install dependencies:

Bash
npm install
Configure the API endpoint in your config (e.g., src/App.jsx):

JavaScript
const API_URL = "http://localhost:8000";
Start the Vite development server:

Bash
npm run dev
🐳 Docker Deployment
To build and run the backend using Docker (as configured for Hugging Face Spaces):

Bash
docker build -t documind-api .
docker run -p 7860:7860 -e GROQ_API_KEY="your_api_key" documind-api
👨‍💻 Author
Pranab Paul

GitHub: @pranab170

B.Tech Computer Science and Engineering, CUTM Bhubaneswar

Note: This is an independent project designed for educational purposes and is not officially affiliated with CUTM's administration.
