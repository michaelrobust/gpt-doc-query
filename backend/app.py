from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import os
import shutil
from datetime import datetime
import uuid

from services.pdf_processor import PDFProcessor
from services.vector_store import VectorStoreService
from services.llm_service import LLMService
from models.query import QueryRequest, QueryResponse
from utils.config import settings

# 創建 FastAPI 應用
app = FastAPI(
    title="RAG Assistant API",
    description="AI-powered document Q&A system with demo mode support",
    version="2.0.0"
)

# CORS 中間件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 初始化服務
print("🚀 Initializing RAG Assistant services...")

try:
    pdf_processor = PDFProcessor()
    print("✅ PDF Processor initialized")
except Exception as e:
    print(f"❌ PDF Processor failed: {e}")
    pdf_processor = None

try:
    vector_store = VectorStoreService()
    print("✅ Vector Store initialized")
except Exception as e:
    print(f"❌ Vector Store failed: {e}")
    vector_store = None

try:
    llm_service = LLMService()
    print("✅ LLM Service initialized")
except Exception as e:
    print(f"❌ LLM Service failed: {e}")
    llm_service = None

@app.get("/")
async def root():
    mode = "Demo Mode" if settings.DEMO_MODE else "Production Mode"
    return {
        "message": "RAG Assistant API is running!",
        "mode": mode,
        "version": "2.0.0",
        "features": {
            "document_upload": pdf_processor is not None,
            "vector_search": vector_store is not None,
            "ai_generation": llm_service is not None,
            "demo_mode": settings.DEMO_MODE
        }
    }

@app.get("/api/health")
async def health_check():
    return {
        "status": "healthy",
        "mode": "demo" if settings.DEMO_MODE else "production",
        "services": {
            "pdf_processor": pdf_processor is not None,
            "vector_store": vector_store is not None,
            "llm_service": llm_service is not None
        }
    }

@app.post("/api/upload")
async def upload_document(file: UploadFile = File(...)):
    try:
        if not pdf_processor:
            raise HTTPException(status_code=503, detail="PDF processor not available")
        
        if not vector_store:
            raise HTTPException(status_code=503, detail="Vector store not available")
        
        # 檢查文件類型
        allowed_extensions = ['.pdf', '.txt', '.docx']
        if not any(file.filename.lower().endswith(ext) for ext in allowed_extensions):
            raise HTTPException(
                status_code=400, 
                detail="Only PDF, TXT, and DOCX files are supported"
            )
        
        # 檢查文件大小
        if file.size > settings.MAX_FILE_SIZE:
            raise HTTPException(
                status_code=400,
                detail=f"File size exceeds maximum limit of {settings.MAX_FILE_SIZE} bytes"
            )
        
        # 生成唯一文件 ID 和路徑
        file_id = str(uuid.uuid4())
        filename = f"{file_id}_{file.filename}"
        file_path = os.path.join(settings.UPLOAD_DIR, filename)
        
        # 創建上傳目錄
        os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
        
        # 保存文件
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        print(f"📁 File saved: {file_path}")
        
        # 處理不同類型的文件
        try:
            if file.filename.lower().endswith('.pdf'):
                text_content = pdf_processor.extract_text(file_path)
            elif file.filename.lower().endswith('.txt'):
                with open(file_path, 'r', encoding='utf-8') as f:
                    text_content = f.read()
            elif file.filename.lower().endswith('.docx'):
                # 如果有 docx 處理器的話
                text_content = pdf_processor.extract_text(file_path)  # 假設 pdf_processor 也能處理 docx
            else:
                raise ValueError("Unsupported file type")
            
            print(f"📄 Extracted text length: {len(text_content)} characters")
            
        except Exception as e:
            # 清理已保存的文件
            if os.path.exists(file_path):
                os.remove(file_path)
            raise HTTPException(status_code=400, detail=f"Failed to extract text: {str(e)}")
        
        # 分割文本
        try:
            chunks = pdf_processor.split_text(text_content)
            print(f"🔪 Text split into {len(chunks)} chunks")
        except Exception as e:
            if os.path.exists(file_path):
                os.remove(file_path)
            raise HTTPException(status_code=500, detail=f"Failed to split text: {str(e)}")
        
        # 添加到向量存儲
        try:
            doc_id = vector_store.add_document(file_id, chunks, file.filename)
            if not doc_id:
                raise Exception("Failed to add document to vector store")
            print(f"🎯 Document added to vector store with ID: {doc_id}")
        except Exception as e:
            if os.path.exists(file_path):
                os.remove(file_path)
            raise HTTPException(status_code=500, detail=f"Failed to vectorize document: {str(e)}")
        
        # 清理臨時文件
        if os.path.exists(file_path):
            os.remove(file_path)
        
        return JSONResponse({
            "success": True,
            "document_id": doc_id,
            "filename": file.filename,
            "chunks_count": len(chunks),
            "file_size": file.size,
            "processing_mode": "demo" if settings.DEMO_MODE else "production",
            "message": f"Successfully processed document with {len(chunks)} chunks"
        })
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Upload error: {e}")
        raise HTTPException(status_code=500, detail=f"Document processing failed: {str(e)}")

@app.post("/api/query")
async def query_documents(request: QueryRequest):
    try:
        if not vector_store:
            raise HTTPException(status_code=503, detail="Vector store not available")
        
        if not llm_service:
            raise HTTPException(status_code=503, detail="LLM service not available")
        
        print(f"🔍 Processing query: {request.query}")
        
        # 搜索相關文檔片段
        relevant_chunks = vector_store.similarity_search(request.query, k=request.top_k)
        
        if not relevant_chunks:
            return {
                "answer": "抱歉，我在文檔中找不到與您問題相關的信息。請嘗試重新表述問題或上傳相關文檔。",
                "sources": [],
                "confidence": 0.0,
                "mode": "demo" if settings.DEMO_MODE else "production"
            }
        
        # 生成回答
        answer = llm_service.generate_answer(
            query=request.query,
            context_chunks=relevant_chunks
        )
        
        # 構建來源信息
        sources = []
        for chunk in relevant_chunks:
            sources.append({
                "content": chunk["content"][:300] + "..." if len(chunk["content"]) > 300 else chunk["content"],
                "document": chunk["document"],
                "similarity_score": chunk.get("similarity_score", 0.0),
                "document_id": chunk.get("document_id", "unknown")
            })
        
        # 計算置信度
        if relevant_chunks:
            avg_similarity = sum(chunk.get("similarity_score", 0) for chunk in relevant_chunks) / len(relevant_chunks)
            confidence = min(0.95, max(0.1, avg_similarity))
        else:
            confidence = 0.0
        
        return {
            "answer": answer,
            "sources": sources,
            "confidence": confidence,
            "chunks_found": len(relevant_chunks),
            "mode": "demo" if settings.DEMO_MODE else "production",
            "query_processed": request.query
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Query error: {e}")
        raise HTTPException(status_code=500, detail=f"Query processing failed: {str(e)}")

@app.get("/api/documents")
async def list_documents():
    try:
        if not vector_store:
            raise HTTPException(status_code=503, detail="Vector store not available")
        
        documents = vector_store.list_documents()
        
        return {
            "documents": documents,
            "total_count": len(documents),
            "mode": "demo" if settings.DEMO_MODE else "production"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Document list error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get document list: {str(e)}")

@app.delete("/api/documents/{document_id}")
async def delete_document(document_id: str):
    """刪除指定文檔（示例端點）"""
    try:
        # 這裡可以實現刪除邏輯
        return {
            "success": True,
            "message": f"Document {document_id} deletion requested",
            "note": "This is a demo endpoint - actual deletion not implemented"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete document: {str(e)}")

# 錯誤處理
@app.exception_handler(404)
async def not_found_handler(request, exc):
    return JSONResponse(
        status_code=404,
        content={"detail": "Endpoint not found", "suggestion": "Check API documentation"}
    )

@app.exception_handler(500)
async def internal_error_handler(request, exc):
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Internal server error", 
            "mode": "demo" if settings.DEMO_MODE else "production",
            "suggestion": "Please check logs for details"
        }
    )