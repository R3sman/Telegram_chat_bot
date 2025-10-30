import requests
import os
from typing import List, Dict, Any
import json
from dotenv import load_dotenv

load_dotenv()

class GigaChatClient:
    def __init__(self):
        self.client_id = os.getenv('GIGACHAT_CLIENT_ID')
        self.client_secret = os.getenv('GIGACHAT_CLIENT_SECRET')
        self.scope = os.getenv('GIGACHAT_SCOPE')
        self.access_token = None
        self.base_url = "https://gigachat.devices.sberbank.ru/api/v1"
        
    def authenticate(self) -> str:
        """Аутентификация в GigaChat API"""
        try:
            # Получаем access token
            auth_url = "https://ngw.devices.sberbank.ru:9443/api/v2/oauth"
            auth_data = {
                'scope': self.scope
            }
            auth_headers = {
                'Content-Type': 'application/x-www-form-urlencoded',
                'Accept': 'application/json'
            }
            
            response = requests.post(
                auth_url,
                data=auth_data,
                headers=auth_headers,
                auth=(self.client_id, self.client_secret),
                verify=False
            )
            
            if response.status_code == 200:
                self.access_token = response.json()['access_token']
                return self.access_token
            else:
                raise Exception(f"Ошибка аутентификации: {response.status_code} - {response.text}")
                
        except Exception as e:
            print(f"Ошибка при аутентификации: {str(e)}")
            raise
    
    def get_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Получает эмбеддинги для списка текстов"""
        if not self.access_token:
            self.authenticate()
            
        url = f"{self.base_url}/embeddings"
        headers = {
            'Authorization': f'Bearer {self.access_token}',
            'Content-Type': 'application/json'
        }
        
        data = {
            "model": "Embeddings",
            "input": texts
        }
        
        try:
            response = requests.post(url, headers=headers, json=data, verify=False)
            if response.status_code == 200:
                result = response.json()
                return [item['embedding'] for item in result['data']]
            else:
                print(f"Ошибка при получении эмбеддингов: {response.status_code}")
                return []
        except Exception as e:
            print(f"Исключение при получении эмбеддингов: {str(e)}")
            return []
    
    def generate_answer(self, question: str, context: str) -> str:
        """Генерирует ответ на основе вопроса и контекста"""
        if not self.access_token:
            self.authenticate()
            
        url = f"{self.base_url}/chat/completions"
        headers = {
            'Authorization': f'Bearer {self.access_token}',
            'Content-Type': 'application/json'
        }
        
        prompt = f"""На основе следующего контекста ответь на вопрос пользователя. 
Если в контексте нет информации для ответа, скажи об этом.

Контекст: {context}

Вопрос: {question}

Ответ:"""
        
        data = {
            "model": "GigaChat",
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "temperature": 0.7,
            "max_tokens": 1000
        }
        
        try:
            response = requests.post(url, headers=headers, json=data, verify=False)
            if response.status_code == 200:
                result = response.json()
                return result['choices'][0]['message']['content']
            else:
                return f"Ошибка при генерации ответа: {response.status_code}"
        except Exception as e:
            return f"Исключение при генерации ответа: {str(e)}"
