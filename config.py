import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """
    Loyiha uchun barcha konfiguratsiyalarni boshqaruvchi klass.
    """
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    SECRET_KEY = os.getenv("SECRET_KEY")
    DEBUG = os.getenv("DEBUG", "True") == "True"
    
    @staticmethod
    def check_config():
        """Barcha muhim kalitlar yuklanganini tekshirish uchun"""
        if not Config.GEMINI_API_KEY:
            raise ValueError("XATO: GEMINI_API_KEY .env faylida topilmadi!")