import ollama 
import requests
import json
from typing import Dict, List
from config.settings import settings

class ResponseFormatterAgent:
    """Агент для формирования ответа с использованием Ollama"""
    
    def __init__(self, model_name: str = None):
        if model_name is None:
            model_name = "qwen2.5:7b" 
        self.model_name = model_name

    def call_ollama(self, messages: List[Dict]) -> str:
        try:
            response = ollama.chat(
                model=self.model_name,
                messages=messages,
                options={
                    "temperature": 0.1,  
                    "num_predict": 500, 
                    "top_k": 20,    
                    "top_p": 0.9,
                    "repeat_penalty": 1.1,
                    "num_ctx": 2048
                },
                stream=False
            )
            
            if hasattr(response, 'message') and hasattr(response.message, 'content'):
                return response.message.content.strip()
            
            return "Неверный формат ответа"
            
        except Exception as e:
            return f"Ошибка: {str(e)[:100]}"
    
    def format_response(self, query: str, context: str) -> str:
        """Формирование окончательного ответа"""
        
        # УСИЛЕННЫЙ русскоязычный системный промпт
        system_prompt = """Ты - автомобильный ассистент. Твоя задача - отвечать на на вопросы автовладельцев.
        
        ТЕХНИЧЕСКИЕ ТРЕБОВАНИЯ:
        1. Отвечай ТОЛЬКО на РУССКОМ ЯЗЫКЕ
        2. Используй ТОЛЬКО информацию из предоставленного контекста
        3. Если информации недостаточно, скажи: "В предоставленном руководстве нет информации по этому вопросу"
        4. Будь точным и технически корректным
        5. Форматируй ответ четко и структурированно
        
        КОНТЕКСТ ИЗ РУКОВОДСТВА:
        {context}
        
        ВОПРОС ПОЛЬЗОВАТЕЛЯ:
        {query}
        
        ОТВЕТ (на русском языке):"""
        
        user_message = f"""Вопрос: {query}

    Контекст из руководства по эксплуатации:
    {context}

    Сформулируй полный и точный ответ на русском языке, используя ТОЛЬКО предоставленную информацию."""
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message}
        ]
        
        return self.call_ollama(messages)
