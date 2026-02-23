
import os
import threading
from flask import Flask
import telebot
from supabase import create_client

# 1. Configuración de variables (Usa variables de entorno en Render)
TOKEN = os.getenv("TELEGRAM_TOKEN")
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

bot = telebot.TeleBot(TOKEN)
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# --- TRUCO PARA RENDER: Servidor Flask ---
app = Flask(__name__)

@app.route('/')
def health_check():
    return "Bot is Alive!", 200

def run_flask():
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))

# --- LÓGICA DEL BOT ---
@bot.message_handler(func=lambda message: True)
def handle_message(message):
    user_text = message.text
    user_id = message.from_user.id
    
    # Guardar en Supabase (tus datos ya no están atrapados)
    data = {"user_id": user_id, "content": user_text}
    supabase.table("mensajes").insert(data).execute()
    
    bot.reply_to(message, "Procesado y guardado en la nube 🚀")

if __name__ == "__main__":
    # Iniciar Flask en un hilo separado
    threading.Thread(target=run_flask).start()
    # Iniciar el Bot
    print("Bot encendido...")
    bot.infinity_polling()
