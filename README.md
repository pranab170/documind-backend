# 🧠 DocuMind - CUTM Document Intelligence Assistant

> An interactive, AI-powered RAG (Retrieval-Augmented Generation) assistant designed to instantly navigate, retrieve, and answer queries regarding the official academic regulations of Centurion University of Technology and Management (CUTM).

![Status](https://img.shields.io/badge/Status-Live-success?style=for-the-badge)
![Python](https://img.shields.io/badge/Python-3.11-blue?style=for-the-badge&logo=python)
![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi)
![React](https://img.shields.io/badge/React-20232A?style=for-the-badge&logo=react&logoColor=61DAFB)
![Hugging Face](https://img.shields.io/badge/Hugging%20Face-Spaces-F58025?style=for-the-badge&logo=huggingface)

---

## 🚀 Project Overview

DocuMind is not just a basic chatbot; it is a custom-built document intelligence system. It reads through complex university rulebooks and provides exact, grounded answers with citations. 

### ✨ Key Features
* **Hybrid Retrieval System:** Combines exact keyword matching (BM25) with semantic meaning search (ChromaDB Vector Store).
* **Reciprocal Rank Fusion (RRF):** Intelligently merges results from both retrieval methods to find the most accurate rule/clause.
* **Source Citations:** Every answer includes the exact document name and text snippet used to generate it.
* **Lightning Fast LLM:** Powered by the Groq API for rapid inference and response generation.

---

## 🛠️ Tech Stack & Architecture

### Frontend (Client-Side)
* **Framework:** React.js (Vite)
* **Styling:** Tailwind CSS (Custom Dark Mode UI)
* **Hosting:** Cloudflare Pages

### Backend (Server-Side)
* **API Framework:** FastAPI (Python)
* **Orchestration:** LangChain
* **Vector Database:** ChromaDB
* **Embeddings:** HuggingFace `sentence-transformers/all-MiniLM-L6-v2`
* **LLM Engine:** Groq API 
* **Deployment:** Dockerized and hosted on Hugging Face Spaces (16GB RAM)

---

## 📂 Project Structure

```text
documind/
├── documind-frontend/       # React UI Code
│   ├── src/                 # React components and pages
│   ├── package.json         # Node dependencies
│   └── vite.config.js       # Vite bundler config
│
├── documind-backend/        # FastAPI & RAG Engine
│   ├── data/                # Contains ChromaDB local storage
│   ├── main.py              # FastAPI application & routes
│   ├── retriever.py         # Hybrid Retriever (BM25 + RRF + Vector)
│   ├── rag_chain.py         # LangChain logic for Groq LLM
│   ├── requirements.txt     # Python dependencies
│   └── Dockerfile           # Deployment config for Hugging Face
## 💻 Local Setup Instructions

### 1. Backend Setup

Navigate to the backend directory and install the required Python libraries:

```bash
cd documind-backend
pip install -r requirements.txt
Create a `.env` file in the `documind-backend` folder and add your Groq API key:

```env
GROQ_API_KEY=gsk_your_actual_api_key_here
GROQ_API_KEY=gsk_your_actual_api_key_here
Start the local API server:

Bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
2. Frontend Setup
Open a new terminal, navigate to the frontend directory, and install Node modules:

Bash
cd documind-frontend
npm install
Configure your local API endpoint inside the React app (e.g., in src/App.jsx):

JavaScript
const API_URL = "http://localhost:8000";
Start the Vite development server:

Bash
npm run dev
👨‍💻 Developer
Pranab Paul

B.Tech Computer Science and Engineering, CUTM Bhubaneswar

GitHub: @pranab170

Disclaimer: This is an independent project designed for educational purposes and is not officially affiliated with CUTM's administration.



