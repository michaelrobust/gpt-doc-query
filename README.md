# GPT-doc-query — Retrieval-Augmented Generation PDF QA App

**RAG Assistant** is an AI-powered assistant built with Retrieval-Augmented Generation (RAG), allowing users to upload PDF documents and interact with them using natural language queries. It integrates OpenAI's LLM, FAISS vector search, and a modern Next.js frontend for a full-stack QA experience.

---

## 📦 Features

✅ Upload and process PDF files in real time  
✅ Convert documents into embeddings and store locally  
✅ Semantic search across multiple documents  
✅ AI answers with cited sources  
✅ Intuitive, integrated frontend and backend experience

---

## 🏗️ System Architecture

Frontend (Next.js)
↕ API Calls
Backend (FastAPI)
↳ PDF Parsing
↳ Vector Store (FAISS)
↳ OpenAI-based Answer Generation

---

## 🔧 Tech Stack

| Layer       | Technologies                     |
|-------------|----------------------------------|
| Frontend    | Next.js, TypeScript, TailwindCSS |
| Backend     | FastAPI, Python 3.10+            |
| LLM         | OpenAI GPT-3.5 or GPT-4           |
| Vector DB   | FAISS                            |
| PDF Parsing | PyMuPDF                          |

---

## 🚀 Getting Started

### 1️⃣ Set up virtual environment and install dependencies

```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

2️⃣ Create .env file

Inside the backend/ folder, create a .env file:

OPENAI_API_KEY=your_api_key
UPLOAD_DIR=./data/uploads
VECTOR_DB_PATH=./data/vector_db

3️⃣ Start the backend server

cd backend
uvicorn app:app --reload

4️⃣ Start the frontend

cd frontend
npm install
npm run dev

Open the app in your browser: http://localhost:3000

⸻

📂 Project Structure

├── backend/
│   ├── app.py                 # FastAPI main entrypoint
│   ├── services/              # Services for PDF, vector DB, and LLM
│   ├── models/                # API request/response schemas
│   ├── utils/                 # Configuration loader
│   └── data/                  # File uploads & vector DB (excluded in Git)
├── frontend/                  # Next.js frontend
│   └── src/components/        # Upload UI, Chat interface, etc.
├── .gitignore
└── README.md


⸻

🛡️ Notes
	•	Do not upload .env or data/ to GitHub
	•	.gitignore already excludes sensitive and large files
	•	For deployment (e.g., Vercel, Docker), you can extend this README later

⸻

🙌 Credits & Contributions

This project serves as a learning demo for LLM and RAG-based applications.
Feel free to fork, modify, or contribute!

Author: @michaelrobust
Made with ❤️ for hackathons, AI demos, and real-world RAG apps.
