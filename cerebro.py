# cerebro.py
from core_game import procesar_jugada
from core_datos import guardar_mensaje

def procesar_mensaje(bot, supabase, message):
    user_id = message.from_user.id
    texto = message.text

    # Guardar SIEMPRE
    guardar_mensaje(supabase, user_id, texto)

    # Decidir qué hacer
    respuesta = procesar_jugada(user_id, texto)

    bot.reply_to(message, respuesta)
