import chromadb
from chromadb.config import Settings as ChromaSettings
from sentence_transformers import SentenceTransformer
import uuid
from typing import List, Dict, Optional

class VectorDatabase:
    """Класс для работы с векторной базой данных ChromaDB"""
    
    def __init__(self, pdf_name: Optional[str] = None):
        """
        Инициализация векторной базы.
        Если указан pdf_name - создается коллекция с уникальным именем для этого PDF.
        """
        self.pdf_name = pdf_name
        self.persist_directory = "data/vector_db/"
        
        # Модель для эмбеддингов
        self.embedding_model = SentenceTransformer(
            "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
        )
        
        # Инициализация ChromaDB
        self.client = chromadb.PersistentClient(
            path=self.persist_directory,
            settings=ChromaSettings(anonymized_telemetry=False)
        )
        
        # УНИКАЛЬНОЕ имя коллекции для каждого PDF
        if pdf_name:
            # Создаем безопасное имя коллекции (убираем расширение .pdf и спецсимволы)
            safe_name = pdf_name.replace('.pdf', '').replace(' ', '_').replace('-', '_').lower()
            collection_name = f"pdf_{safe_name}"
        else:
            collection_name = "pdf_default"
        
        # Создание или получение коллекции
        self.collection = self.client.get_or_create_collection(
            name=collection_name,
            metadata={
                "hnsw:space": "cosine",
                "source_pdf": pdf_name if pdf_name else "default"
            }
        )
        
        print(f"📁 Коллекция: '{collection_name}' (PDF: {pdf_name or 'default'})")
    
    def create_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Создание эмбеддингов для текстов"""
        return self.embedding_model.encode(texts).tolist()
    
    def add_documents(self, documents: List[Dict]):
        """Добавление документов в векторную базу"""
        if not self.pdf_name:
            raise ValueError("Не указано имя PDF для добавления документов")
        
        texts = [doc["text"] for doc in documents]
        metadatas = [
            {
                "source": self.pdf_name,
                "page": doc.get("page", 0),
                "chunk_id": str(uuid.uuid4())[:8]
            } 
            for doc in documents
        ]
        
        embeddings = self.create_embeddings(texts)
        ids = [str(uuid.uuid4()) for _ in range(len(texts))]
        
        self.collection.add(
            embeddings=embeddings,
            documents=texts,
            metadatas=metadatas,
            ids=ids
        )
        
        print(f"✅ Добавлено {len(documents)} чанков в коллекцию для '{self.pdf_name}'")
    
    def search(self, query: str, n_results: int = 5) -> List[Dict]:
        """Поиск релевантных документов в текущей коллекции"""
        if not self.collection.count():
            return []  # Коллекция пуста
        
        query_embedding = self.create_embeddings([query])[0]
        
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results,
            include=["documents", "metadatas", "distances"]
        )
        
        formatted_results = []
        if results["documents"] and len(results["documents"][0]) > 0:
            for i in range(len(results["documents"][0])):
                formatted_results.append({
                    "text": results["documents"][0][i],
                    "metadata": results["metadatas"][0][i],
                    "score": 1 - results["distances"][0][i]
                })
        
        return formatted_results
    
    def get_collection_info(self) -> Dict:
        """Получение информации о коллекции"""
        return {
            "name": self.collection.name,
            "pdf_name": self.pdf_name,
            "count": self.collection.count(),
            "metadata": self.collection.metadata
        }