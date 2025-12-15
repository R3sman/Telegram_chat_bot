from typing import Dict, Any, Optional
from agents.pdf_analyzer import PDFAnalyzerAgent
from agents.search_agent import SearchAgent
from agents.response_formatter import ResponseFormatterAgent
from database.vector_store import VectorDatabase
from config.settings import settings

class CoordinatorAgent:
    """Главный агент, координирующий работу всех агентов"""
    
    def __init__(self):
        self.vector_db: Optional[VectorDatabase] = None
        self.pdf_analyzer = PDFAnalyzerAgent("data/pdf_files/")
        self.search_agent = SearchAgent(None) 
        self.response_formatter = ResponseFormatterAgent(
            model_name=settings.OLLAMA_MODEL
        )
        
        self.pdf_loaded = False
        self.current_pdf = None
    
    def load_pdf(self, pdf_filename: str) -> str:
        """Загрузка и индексация PDF-файла в отдельную коллекцию"""
        try:
            print(f"Извлечение текста из '{pdf_filename}'...")
            documents = self.pdf_analyzer.process_pdf(pdf_filename)
            
            print(f"Создание векторной базы '{pdf_filename}'...")
            self.vector_db = VectorDatabase(pdf_name=pdf_filename)
            
            self.vector_db.add_documents(documents)
            
            self.search_agent = SearchAgent(self.vector_db)
            
            self.pdf_loaded = True
            self.current_pdf = pdf_filename
            
            total_chars = sum(len(doc["text"]) for doc in documents)
            collection_info = self.vector_db.get_collection_info()
            
            return (f"PDF '{pdf_filename}' успешно загружен!\n\n"
                   f"Теперь можете задавать вопросы по этому руководству.")
                   
        except FileNotFoundError:
            return f"Файл '{pdf_filename}' не найден в папке data/pdf_files/"
        except Exception as e:
            return f"Ошибка при загрузке PDF: {str(e)}"
    
    def process_query(self, user_query: str) -> str:
        if not self.pdf_loaded or not self.vector_db:
            return "Пожалуйста, сначала загрузите PDF-файл с помощью команды /load_pdf"
        
        RELEVANCE_THRESHOLD = 0.7
        
        search_results = self.search_agent.search_relevant_info(user_query, n_results=10)
        
        if not search_results:
            return "В руководстве не найдено информации по вашему вопросу."
        
        high_relevance_results = [
            r for r in search_results if r["score"] >= RELEVANCE_THRESHOLD
        ]
        
        if not high_relevance_results:
            best_result = max(search_results, key=lambda x: x["score"])
            if best_result["score"] < 0.5:
                return "Не найдено достаточно точной информации в документе."
            high_relevance_results = [best_result]
        
        context = self.search_agent.format_search_results(high_relevance_results[:5])
        response = self.response_formatter.format_response(user_query, context)
        
        if high_relevance_results:
            first_page = high_relevance_results[0]['metadata'].get('page', '?')
            response += f"\n\n Страница: {first_page}"
        
        return response
    
    def get_system_status(self) -> Dict[str, Any]:
        """Получение статуса системы"""
        status = {
            "pdf_loaded": self.pdf_loaded,
            "current_pdf": self.current_pdf,
            "agents_status": "all_running",
            "ollama_model": settings.OLLAMA_MODEL
        }
        
        if self.vector_db:
            collection_info = self.vector_db.get_collection_info()
            status.update({
                "vector_db_status": "active",
                "collection_name": collection_info["name"],
                "documents_count": collection_info["count"]
            })
        else:
            status["vector_db_status"] = "not_initialized"
        
        return status