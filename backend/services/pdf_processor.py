import PyPDF2
import pdfplumber
from typing import List
from langchain.text_splitter import RecursiveCharacterTextSplitter

class PDFProcessor:
    def __init__(self):
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=100,
            separators=["\n\n", "\n", " ", ""]
        )
        print("✅ PDF Processor initialized")

    def extract_text(self, file_path: str) -> str:
        text = ""
        try:
            # First try with pdfplumber (better text extraction)
            with pdfplumber.open(file_path) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
            print(f"✅ Extracted {len(text)} characters using pdfplumber")
        except Exception as e:
            print(f"⚠️ pdfplumber failed: {e}, trying PyPDF2...")
            # Fallback to PyPDF2
            try:
                with open(file_path, 'rb') as file:
                    pdf_reader = PyPDF2.PdfReader(file)
                    for page in pdf_reader.pages:
                        page_text = page.extract_text()
                        if page_text:
                            text += page_text + "\n"
                print(f"✅ Extracted {len(text)} characters using PyPDF2")
            except Exception as e2:
                print(f"❌ Both PDF extractors failed: {e2}")
                raise Exception(f"Could not extract text from PDF: {e2}")
        
        if not text.strip():
            raise Exception("No text could be extracted from the PDF")
        
        return text.strip()

    def split_text(self, text: str) -> List[dict]:
        if not text or not text.strip():
            return []
        
        chunks = self.text_splitter.split_text(text)
        processed_chunks = []
        
        for i, chunk in enumerate(chunks):
            processed_chunks.append({
                "content": chunk.strip(),
                "chunk_index": i,
                "length": len(chunk),
                "start_char": 0,  # Could be calculated if needed
                "end_char": len(chunk)
            })
        
        print(f"✅ Split text into {len(processed_chunks)} chunks")
        return processed_chunks