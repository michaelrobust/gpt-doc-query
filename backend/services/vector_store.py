import os
import json
from typing import List, Dict, Any
import faiss
import numpy as np
from datetime import datetime
from utils.config import settings


if settings.DEMO_MODE:
    print("🎭 Loading Demo Embedding Service...")
    try:
        from services.demo_embedding_service import DemoEmbeddingService
        EMBEDDING_SERVICE = "demo"
    except ImportError:
        print("❌ Demo embedding service not found")
        EMBEDDING_SERVICE = None
else:
    try:
        from langchain_openai import OpenAIEmbeddings
        EMBEDDING_SERVICE = "openai"
        print("📦 OpenAI imports successful")
    except Exception as e:
        print(f"❌ OpenAI import failed: {e}")
        try:
            from sentence_transformers import SentenceTransformer
            EMBEDDING_SERVICE = "sentence_transformers"
            print("📦 Falling back to Sentence Transformers")
        except ImportError:
            print("❌ No embedding service available")
            EMBEDDING_SERVICE = None

class VectorStoreService:
    def __init__(self):
        self.embeddings = None
        self.embedding_dim = 1536  # Default OpenAI dimension
        
        
        if EMBEDDING_SERVICE == "demo":
            try:
                self.embeddings = DemoEmbeddingService()
                self.embedding_dim = 384
                print("✅ Demo Embedding Service initialized")
            except Exception as e:
                print(f"❌ Demo embedding service failed: {e}")
                
        elif EMBEDDING_SERVICE == "openai":
            try:
                self.embeddings = OpenAIEmbeddings(
                    openai_api_key=settings.OPENAI_API_KEY,
                    model="text-embedding-ada-002"
                )
                self.embedding_dim = 1536
                print("✅ OpenAI Embeddings initialized successfully")
            except Exception as e:
                print(f"❌ OpenAI Embeddings initialization failed: {e}")
                
        elif EMBEDDING_SERVICE == "sentence_transformers":
            try:
                self.embeddings = SentenceTransformer('all-MiniLM-L6-v2')
                self.embedding_dim = 384
                print("✅ Sentence Transformers initialized")
            except Exception as e:
                print(f"❌ Sentence Transformers failed: {e}")
        
        if not self.embeddings:
            print("⚠️ No embedding service available")
            
        self.index_path = os.path.join(settings.VECTOR_DB_PATH, "faiss_index")
        self.metadata_path = os.path.join(settings.VECTOR_DB_PATH, "metadata.json")
        
        os.makedirs(settings.VECTOR_DB_PATH, exist_ok=True)
        
        self.index = None
        self.metadata = {}
        self._load_or_create_index()
    
    def _load_or_create_index(self):
        if os.path.exists(self.index_path):
            try:
                self.index = faiss.read_index(self.index_path)
                if os.path.exists(self.metadata_path):
                    with open(self.metadata_path, 'r', encoding='utf-8') as f:
                        self.metadata = json.load(f)
                print(f"✅ Existing vector index loaded with {self.index.ntotal} vectors")
            except Exception as e:
                print(f"⚠️ Error loading existing index: {e}")
                self._create_new_index()
        else:
            self._create_new_index()
    
    def _create_new_index(self):
        
        if EMBEDDING_SERVICE == "demo" or EMBEDDING_SERVICE == "sentence_transformers":
            self.index = faiss.IndexFlatIP(384)  
        else:
            self.index = faiss.IndexFlatL2(1536) 
        self.metadata = {"documents": {}, "chunks": []}
        print("✅ New vector index created")
    
    def add_document(self, doc_id: str, chunks: List[dict], filename: str) -> str:
        if not self.embeddings:
            print("⚠️ No embedding service available")
            return None
            
        try:
            texts = [chunk["content"] for chunk in chunks]
            print(f"🔄 Generating embeddings for {len(texts)} text chunks...")
            
            
            if EMBEDDING_SERVICE == "demo":
                embeddings = self.embeddings.generate_embeddings(texts)
            elif EMBEDDING_SERVICE == "openai":
                embeddings = self.embeddings.embed_documents(texts)
                embeddings = np.array(embeddings).astype('float32')
            elif EMBEDDING_SERVICE == "sentence_transformers":
                embeddings = self.embeddings.encode(texts)
                embeddings = np.array(embeddings).astype('float32')
            else:
                raise Exception("No valid embedding service")
            
            print(f"✅ Successfully generated embeddings for {len(texts)} chunks")
            
            
            if EMBEDDING_SERVICE in ["demo", "sentence_transformers"]:
                faiss.normalize_L2(embeddings)
            
        except Exception as e:
            print(f"❌ Embedding generation failed: {e}")
            return None
        
        try:
            start_idx = self.index.ntotal
            self.index.add(embeddings)
            
            self.metadata["documents"][doc_id] = {
                "filename": filename,
                "upload_time": str(datetime.now()),
                "chunk_count": len(chunks),
                "start_idx": start_idx,
                "end_idx": start_idx + len(chunks)
            }
            
            for i, chunk in enumerate(chunks):
                self.metadata["chunks"].append({
                    "document_id": doc_id,
                    "chunk_index": i,
                    "faiss_index": start_idx + i,
                    "content": chunk["content"],
                    "filename": filename
                })
            
            self._save_index()
            print(f"✅ Document '{filename}' successfully added to vector store")
            return doc_id
            
        except Exception as e:
            print(f"❌ Failed to add document: {e}")
            return None
    
    def similarity_search(self, query: str, k: int = 5) -> List[dict]:
        if not self.embeddings or self.index.ntotal == 0:
            print("⚠️ No embeddings available or empty index")
            return []
        
        try:
            print(f"🔍 Searching for query: '{query}'")
            
            
            if EMBEDDING_SERVICE == "demo":
                query_embedding = self.embeddings.generate_embeddings([query])
                query_vector = query_embedding.astype('float32')
            elif EMBEDDING_SERVICE == "openai":
                query_embedding = self.embeddings.embed_query(query)
                query_vector = np.array([query_embedding]).astype('float32')
            elif EMBEDDING_SERVICE == "sentence_transformers":
                query_embedding = self.embeddings.encode([query])
                query_vector = np.array(query_embedding).astype('float32')
            else:
                raise Exception("No valid embedding service")
            
            
            if EMBEDDING_SERVICE in ["demo", "sentence_transformers"]:
                faiss.normalize_L2(query_vector)
            
            distances, indices = self.index.search(query_vector, k)
            
            results = []
            for i, idx in enumerate(indices[0]):
                if idx < len(self.metadata["chunks"]):
                    chunk_info = self.metadata["chunks"][idx]
                    
                    
                    if EMBEDDING_SERVICE in ["demo", "sentence_transformers"]:
                        similarity_score = float(distances[0][i]) 
                    else:
                        similarity_score = 1.0 / (1.0 + float(distances[0][i]))  
                    
                    results.append({
                        "content": chunk_info["content"],
                        "document": chunk_info["filename"],
                        "document_id": chunk_info["document_id"],
                        "similarity_score": similarity_score
                    })
            
            print(f"✅ Found {len(results)} relevant chunks")
            return results
            
        except Exception as e:
            print(f"❌ Search failed: {e}")
            return []
    
    def list_documents(self) -> List[dict]:
        return [
            {
                "document_id": doc_id,
                "filename": info["filename"],
                "upload_time": info["upload_time"],
                "chunk_count": info["chunk_count"]
            }
            for doc_id, info in self.metadata["documents"].items()
        ]
    
    def _save_index(self):
        try:
            faiss.write_index(self.index, self.index_path)
            with open(self.metadata_path, 'w', encoding='utf-8') as f:
                json.dump(self.metadata, f, ensure_ascii=False, indent=2)
            print("✅ Vector index saved successfully")
        except Exception as e:
            print(f"❌ Failed to save index: {e}")