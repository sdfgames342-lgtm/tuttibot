import telebot
import os
from dotenv import load_dotenv
from telebot import types

# Cargar variables desde el nivel superior
load_dotenv(os.path.join(os.path.dirname(__file__), '../../.env'))

class ItsukiBot:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ItsukiBot, cls).__new__(cls)
            
            # Obtener token desde .env
            token = os.getenv('TELEGRAM_TOKEN')
            
            if not token:
                raise ValueError("❌ ERROR: No se encontró TELEGRAM_TOKEN en el archivo .env")
            
            cls._instance.bot = telebot.TeleBot(token, parse_mode=None)
            cls._instance._patch_reply_methods()
            
        return cls._instance

    def _patch_reply_methods(self):
        """Parche de seguridad para evitar crasheos por errores de formato en mensajes"""
        original_send_message = self.bot.send_message
        def safe_send_message(*args, **kwargs):
            try:
                return original_send_message(*args, **kwargs)
            except Exception as e:
                if "can't parse" in str(e):
                    kwargs['parse_mode'] = None
                    return original_send_message(*args, **kwargs)
                raise e
        self.bot.send_message = safe_send_message

    def get_instance(self):
        return self.bot
