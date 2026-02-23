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
# 1. Asegúrate de leer la variable al inicio
CREATOR_ID = int(os.getenv("CREATOR_ID", 0))

def registrar_usuario(message):
    t_id = message.from_user.id
    
    # Verificar si ya existe en el historial
    res = supabase.table("id_history").select("cus").eq("telegram_id", t_id).execute()
    
    if not res.data:
        nuevo_cus = generar_cus() # La función de 26 caracteres
        
        # DETERMINAR SI ES ADMIN:
        # Si el ID coincide con el que pusiste en Render, es admin
        es_jefe = (t_id == CREATOR_ID)
        
        # 1. Crear en tabla 'users' con sus estadísticas en 0
        supabase.table("users").insert({
            "cus": nuevo_cus,
            "es_admin": es_jefe, # <--- AQUÍ se asigna el poder
            "puntos_total": 0,
            "idioma": "es"
        }).execute()
        
        # 2. Vincular el Telegram ID al CUS
        supabase.table("id_history").insert({
            "telegram_id": t_id,
            "cus": nuevo_cus
        }).execute()
        
        prefijo = "👑 ADMIN RECONOCIDO" if es_jefe else "👤 USUARIO REGISTRADO"
        return f"{prefijo}\nTu CUS: `{nuevo_cus}`"
    
    return "Ya estás en la base de datos."
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
