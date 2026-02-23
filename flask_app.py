import os
import threading
import random
import string
from flask import Flask
import telebot
from supabase import create_client

# ================== CONFIG ==================
TOKEN = os.getenv("TELEGRAM_TOKEN")
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
CREATOR_ID = int(os.getenv("CREATOR_ID", 0))

if not all([TOKEN, SUPABASE_URL, SUPABASE_KEY]):
    raise RuntimeError("❌ Faltan variables de entorno")

bot = telebot.TeleBot(TOKEN, parse_mode="Markdown")
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# ================== UTIL ==================
def generar_cus():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=26))

def registrar_usuario(message):
    t_id = message.from_user.id
    
    res = supabase.table("id_history").select("cus").eq("telegram_id", t_id).execute()
    
    if not res.data:
        nuevo_cus = generar_cus()
        es_jefe = (t_id == CREATOR_ID)
        
        supabase.table("users").insert({
            "cus": nuevo_cus,
            "es_admin": es_jefe,
            "puntos_total": 0,
            "idioma": "es"
        }).execute()
        
        supabase.table("id_history").insert({
            "telegram_id": t_id,
            "cus": nuevo_cus
        }).execute()
        
        prefijo = "👑 *ADMIN RECONOCIDO*" if es_jefe else "👤 *USUARIO REGISTRADO*"
        return f"{prefijo}\nTu CUS: `{nuevo_cus}`"
    
    return None

# ================== FLASK (RENDER) ==================
app = Flask(__name__)

@app.route('/')
def health_check():
    return "Bot is Alive!", 200

def run_flask():
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))

# ================== BOT ==================
@bot.message_handler(func=lambda m: True)
def handle_message(message):
    user_id = message.from_user.id
    user_text = message.text
    
    registro = registrar_usuario(message)
    if registro:
        bot.reply_to(message, registro)
    
    supabase.table("mensajes").insert({
        "user_id": user_id,
        "content": user_text
    }).execute()
    
    bot.reply_to(message, "Procesado y guardado en la nube 🚀")

# ================== MAIN ==================
if __name__ == "__main__":
    threading.Thread(target=run_flask, daemon=True).start()
    print("🤖 Bot encendido...")
    bot.infinity_polling()
