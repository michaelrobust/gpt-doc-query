from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime

app = FastAPI(
    title="RAG Assistant API Test Version",
    description="Test version without OpenAI dependency",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "RAG Assistant Test API is running!", "status": "OK"}

@app.post("/api/upload")
async def upload_test(file: UploadFile = File(...)):
    return {
        "success": True,
        "document_id": "test-123",
        "filename": file.filename,
        "chunks_count": 5,
        "message": f"Successfully processed document: {file.filename}"
    }

@app.post("/api/query")
async def query_test(request: dict):
    query = request.get("query", "")
    return {
        "answer": f"This is a test response for your question: '{query}'. In the full version, this would provide accurate answers based on uploaded PDF content.",
        "sources": [
            {
                "content": "This is a sample source content from document...",
                "document": "test.pdf",
                "page": 1
            }
        ],
        "confidence": 0.8
    }

@app.get("/api/documents")
async def list_test():
    return {
        "documents": [
            {
                "document_id": "test-123",
                "filename": "sample_document.pdf",
                "upload_time": str(datetime.now()),
                "chunk_count": 5
            }
        ]
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
