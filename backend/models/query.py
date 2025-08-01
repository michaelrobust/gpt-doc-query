from pydantic import BaseModel, Field
from typing import List, Optional

class QueryRequest(BaseModel):
    query: str = Field(..., description="The question to ask about the documents", min_length=1)
    top_k: Optional[int] = Field(default=5, description="Number of chunks to retrieve", ge=1, le=20)
    
    class Config:
        schema_extra = {
            "example": {
                "query": "What is machine learning?",
                "top_k": 5
            }
        }

class SourceInfo(BaseModel):
    content: str = Field(..., description="Content of the source chunk")
    document: str = Field(..., description="Source document name")
    page: Optional[int] = Field(default=None, description="Page number if available")
    similarity_score: Optional[float] = Field(default=None, description="Similarity score")
    document_id: Optional[str] = Field(default=None, description="Document ID")
    
    class Config:
        schema_extra = {
            "example": {
                "content": "Machine learning is a subset of AI...",
                "document": "ml_guide.pdf", 
                "page": 1,
                "similarity_score": 0.95,
                "document_id": "doc_123"
            }
        }

class QueryResponse(BaseModel):
    answer: str = Field(..., description="Generated answer")
    sources: List[SourceInfo] = Field(default=[], description="Source chunks used")
    confidence: float = Field(..., description="Confidence score", ge=0.0, le=1.0)
    chunks_found: Optional[int] = Field(default=None, description="Number of chunks found")
    mode: Optional[str] = Field(default=None, description="Operating mode")
    query_processed: Optional[str] = Field(default=None, description="Processed query")
    
    class Config:
        schema_extra = {
            "example": {
                "answer": "Machine learning is a method of data analysis...",
                "sources": [],
                "confidence": 0.85,
                "chunks_found": 3,
                "mode": "demo",
                "query_processed": "What is machine learning?"
            }
        }

# Additional models for upload responses
class UploadResponse(BaseModel):
    success: bool
    document_id: str
    filename: str
    chunks_count: int
    message: str
    file_size: Optional[int] = None
    processing_mode: Optional[str] = None

class DocumentInfo(BaseModel):
    document_id: str
    filename: str
    upload_time: str
    chunk_count: int

class DocumentListResponse(BaseModel):
    documents: List[DocumentInfo]
    total_count: Optional[int] = None
    mode: Optional[str] = None