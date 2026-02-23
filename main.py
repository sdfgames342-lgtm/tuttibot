# main.py
import os
import telebot
from supabase import create_client

from cerebro import procesar_mensaje
from comandos import registrar_comandos

TOKEN = os.getenv("TELEGRAM_TOKEN")
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

bot = telebot.TeleBot(TOKEN)
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# Registrar comandos
registrar_comandos(bot, supabase)

@bot.message_handler(func=lambda m: True)
def handler(message):
    procesar_mensaje(bot, supabase, message)

print("🤖 Bot iniciado")

try:
    bot.infinity_polling(timeout=60, long_polling_timeout=60)
except Exception as e:
    print("⚠️ Error en polling:", e)
