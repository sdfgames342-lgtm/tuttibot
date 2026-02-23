# main.py
import os
import telebot
from supabase import create_client
import time

from cerebro import procesar_mensaje
from comandos import registrar_comandos

# --- Configuración ---
TOKEN = os.getenv("TELEGRAM_TOKEN")
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

bot = telebot.TeleBot(TOKEN)
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# Registrar todos los comandos
registrar_comandos(bot, supabase)

# Mensajes normales (no comandos)
@bot.message_handler(func=lambda m: True)
def handler(message):
    try:
        procesar_mensaje(bot, supabase, message)
    except Exception as e:
        print("⚠️ Error en procesar_mensaje:", e)
        bot.reply_to(message, "❌ Hubo un error procesando tu mensaje.")

# --- Polling seguro para beta ---
print("🤖 Bot iniciado. Esperando mensajes...")

while True:
    try:
        # timeout en segundos para cada polling
        bot.infinity_polling(timeout=60, long_polling_timeout=60)
    except Exception as e:
        # Captura cualquier error de conexión o 409
        print("⚠️ Error en polling:", e)
        print("⏱ Reintentando en 5 segundos...")
        time.sleep(5)
