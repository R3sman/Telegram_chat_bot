import fitz
import os
from typing import List, Dict

class PDFAnalyzerAgent:
    def __init__(self, pdf_folder: str):
        self.pdf_folder = pdf_folder
    
    def extract_text_from_pdf(self, pdf_path: str) -> List[Dict]:
        doc = fitz.open(pdf_path)
        documents = []
        
        for page_num in range(len(doc)):
            page = doc[page_num]
            text = page.get_text()
            
            if text.strip():
                documents.append({
                    "text": text.strip(),
                    "page": page_num + 1,
                    "source": os.path.basename(pdf_path)
                })
        
        doc.close()
        return documents
    
    def chunk_documents(self, documents: List[Dict], chunk_size: int = 1000, 
                        chunk_overlap: int = 200) -> List[Dict]:
        chunks = []
        
        for doc in documents:
            text = doc["text"]
            words = text.split()
            
            for i in range(0, len(words), chunk_size - chunk_overlap):
                chunk_words = words[i:i + chunk_size]
                chunk_text = ' '.join(chunk_words)
                
                chunks.append({
                    "text": chunk_text,
                    "page": doc["page"],
                    "source": doc["source"]
                })
        
        return chunks
    
    def process_pdf(self, pdf_filename: str) -> List[Dict]:
        pdf_path = os.path.join(self.pdf_folder, pdf_filename)
        
        if not os.path.exists(pdf_path):
            raise FileNotFoundError(f"PDF файл не найден: {pdf_path}")
        
        documents = self.extract_text_from_pdf(pdf_path)
        chunks = self.chunk_documents(documents)
        
        return chunks