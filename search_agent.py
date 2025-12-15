from typing import List, Dict

class SearchAgent:
    """Агент для поиска релевантной информации в базе знаний"""
    
    def __init__(self, vector_db):
        self.vector_db = vector_db
    
    def search_relevant_info(self, query: str, n_results: int = 5) -> List[Dict]:
        """Поиск релевантной информации по запросу"""
        if not self.vector_db:
            return []
        
        search_results = self.vector_db.search(query, n_results)
        
        # Простая фильтрация по релевантности
        filtered_results = [
            result for result in search_results 
            if result["score"] > 0.7
        ]
        
        return filtered_results[:n_results]
    
    def format_search_results(self, results: List[Dict]) -> str:
        """Форматирование результатов поиска для LLM"""
        if not results:
            return "Релевантная информация не найдена в документе."
        
        formatted = "ИНФОРМАЦИЯ ИЗ РУКОВОДСТВА ПО ЭКСПЛУАТАЦИИ:\n\n"
        
        for i, result in enumerate(results, 1):
            formatted += f"БЛОК {i}:\n"
            formatted += f"Страница: {result['metadata'].get('page', 'не указана')}\n"
            formatted += f"Релевантность: {result['score']:.2f}\n"
            formatted += f"Текст: {result['text']}\n"
            formatted += "-" * 50 + "\n"
        
        formatted += "\nВАЖНО: Используй ТОЛЬКО эту информацию для ответа."
        
        return formatted