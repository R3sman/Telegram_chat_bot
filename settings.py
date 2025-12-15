import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    
    
    OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "qwen2.5:7b")
    
   
    TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
    
    
    PDF_FOLDER = "data/pdf_files/"
    VECTOR_DB_PATH = "data/vector_db/"
    
    
    CHUNK_SIZE = 1000
    CHUNK_OVERLAP = 200

settings = Settings()
