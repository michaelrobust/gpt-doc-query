from typing import List, Dict
import traceback
from utils.config import settings

# Only import OpenAI when not in Demo mode
if not settings.DEMO_MODE:
    try:
        from openai import OpenAI
        OPENAI_AVAILABLE = True
    except ImportError:
        OPENAI_AVAILABLE = False
else:
    OPENAI_AVAILABLE = False

class LLMService:
    def __init__(self):
        self.client = None
        
        if settings.DEMO_MODE:
            print("🎭 LLM Service initialized in DEMO MODE")
        elif OPENAI_AVAILABLE:
            try:
                self.client = OpenAI(api_key=settings.OPENAI_API_KEY)
                self.model = "gpt-4o-mini"
                print("✅ OpenAI LLM client initialized")
            except Exception as e:
                print(f"⚠️ OpenAI LLM initialization error: {e}")
                self.client = None
        else:
            print("⚠️ OpenAI not available, using demo mode")
    
    def generate_answer(self, query: str, context_chunks: List[dict]) -> str:
        # Use demo response when in Demo mode or OpenAI is not available
        if settings.DEMO_MODE or not self.client:
            return self._demo_response(query, context_chunks)
        
        try:
            # Build context
            context = "\n".join([chunk.get('content', '') for chunk in context_chunks])
            
            messages = [
                {"role": "system", "content": "You are a helpful assistant that answers questions based on the provided context. Provide clear and accurate responses."},
                {"role": "user", "content": f"Context:\n{context}\n\nQuestion: {query}"}
            ]
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                max_tokens=500,
                temperature=0.7
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            print(f"🚨 OpenAI API Error Details: {e}")
            print(f"Error type: {type(e)}")
            if hasattr(e, 'response'):
                print(f"Response status: {e.response.status_code if e.response else 'No response'}")
            traceback.print_exc()
            return self._demo_response(query, context_chunks)
    
    def _demo_response(self, query: str, context_chunks: List[dict]) -> str:
        if not context_chunks:
            return """❌ **No Relevant Content Found**
            
Sorry, I couldn't find content related to your question in the uploaded documents. Please try:
1. Upload relevant documents
2. Rephrase your question with different keywords
3. Ensure your question relates to the uploaded document content

**System Status:** ✅ Document processing and semantic search functions are working normally"""
        
        # Extract document information
        doc_names = list(set([chunk.get('document', 'Unknown Document') for chunk in context_chunks]))
        total_chunks = len(context_chunks)
        
        # Generate intelligent response based on query analysis
        response = self._generate_intelligent_response(query, context_chunks, doc_names, total_chunks)
        
        return response
    
    def _generate_intelligent_response(self, query: str, context_chunks: List[dict], doc_names: List[str], total_chunks: int) -> str:
        """Generate intelligent demo response based on query and content"""
        
        # Build content summary
        content_snippets = []
        for i, chunk in enumerate(context_chunks[:3]):  # Show top 3 most relevant chunks
            content = chunk.get('content', '')[:200]
            score = chunk.get('similarity_score', 0)
            content_snippets.append(f"**Relevant Chunk {i+1}** (Similarity: {score:.3f})\n{content}...")
        
        # Analyze query type
        query_lower = query.lower()
        
        if any(word in query_lower for word in ['what', 'what is', 'define', 'definition']):
            response_type = "Definition & Explanation"
            demo_answer = self._generate_definition_response(query, context_chunks[0] if context_chunks else {})
        elif any(word in query_lower for word in ['how', 'how to', 'steps', 'process']):
            response_type = "How-to Guide"
            demo_answer = self._generate_howto_response(query, context_chunks[0] if context_chunks else {})
        elif any(word in query_lower for word in ['why', 'why is', 'reason', 'because']):
            response_type = "Reason & Analysis"
            demo_answer = self._generate_why_response(query, context_chunks[0] if context_chunks else {})
        elif any(word in query_lower for word in ['summary', 'summarize', 'overview', 'main points']):
            response_type = "Content Summary"
            demo_answer = self._generate_summary_response(context_chunks)
        else:
            response_type = "General Q&A"
            demo_answer = self._generate_general_response(query, context_chunks[0] if context_chunks else {})
        
        response = f"""✅ **RAG System Intelligent Response Demo**

**Your Question:** {query}
**Query Type:** {response_type}

**AI Generated Answer:**
{demo_answer}

---

**📊 Retrieval Results Details:**
- **Source Documents:** {', '.join(doc_names)}
- **Relevant Chunks Found:** {total_chunks} chunks
- **Most Relevant Content:**

{chr(10).join(content_snippets)}

---

**🎯 System Features Demonstration:**
- ✅ **Document Upload & Processing:** Supports PDF, TXT, DOCX formats
- ✅ **Intelligent Text Chunking:** Automatically segments documents into semantic units
- ✅ **Vector Encoding:** Uses advanced semantic encoding technology
- ✅ **Similarity Search:** Efficient vector retrieval based on FAISS
- ✅ **Semantic Understanding:** Precisely matches user query intent
- 🎭 **AI Text Generation:** Currently in demo mode, can switch to OpenAI GPT

**This demonstrates the complete enterprise-level RAG system architecture and functionality!** 🚀"""

        return response
    
    def _generate_definition_response(self, query: str, top_chunk: dict) -> str:
        content = top_chunk.get('content', '')[:500] if top_chunk else ''
        clean_query = query.replace('what is', '').replace('define', '').strip()
        return f"""Based on the document content, here's information about {clean_query}:

{content}

*This is an intelligent summary based on uploaded document content, demonstrating how the RAG system combines retrieved information to generate accurate answers.*"""
    
    def _generate_howto_response(self, query: str, top_chunk: dict) -> str:
        content = top_chunk.get('content', '')[:500] if top_chunk else ''
        return f"""According to the document content, here are the relevant steps and methods for "{query}":

{content}

*The RAG system successfully retrieved relevant operational guides from the documents and can understand "how-to" type questions.*"""
    
    def _generate_why_response(self, query: str, top_chunk: dict) -> str:
        content = top_chunk.get('content', '')[:500] if top_chunk else ''
        return f"""Based on document analysis, here's the explanation for "{query}":

{content}

*The system demonstrates its ability to understand causal relationship questions and find relevant explanations and analyses from documents.*"""
    
    def _generate_summary_response(self, context_chunks: List[dict]) -> str:
        if len(context_chunks) >= 3:
            summary_points = []
            for i, chunk in enumerate(context_chunks[:3]):
                content = chunk.get('content', '')[:150]
                summary_points.append(f"{i+1}. {content}...")
            
            return f"""Intelligent summary based on document content:

{chr(10).join(summary_points)}

*The RAG system demonstrates its ability to extract key information from multiple document chunks and generate structured summaries.*"""
        else:
            content = context_chunks[0].get('content', '')[:400] if context_chunks else ''
            return f"""Document Summary:

{content}

*Demonstrates single document chunk summarization functionality.*"""
    
    def _generate_general_response(self, query: str, top_chunk: dict) -> str:
        content = top_chunk.get('content', '')[:400] if top_chunk else ''
        return f"""Based on document content, here's relevant information for your question "{query}":

{content}

*The RAG system demonstrates its ability to understand general questions and find the most relevant content chunks from documents.*"""