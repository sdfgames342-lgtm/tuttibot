from telebot import types
from utils.reply_helper import safe_reply
from core.db import registrar_jugador, jugador_en_otra_sala
from utils.idiomas import obtener_texto, formatear_texto
import logging

logger = logging.getLogger(__name__)

HELP_COMMANDS = [
    {"command": "/unir", "desc_key": "help.desc_unir", "sudo_level": 0, "category": "juegos"}
]

def register_unir_handlers(bot, register_command=None, salas=None, salas_lock=None):
    if salas is None:
        return

    @bot.message_handler(commands=['unir'])
    def unir_jugador(message):
        chat_id = str(message.chat.id)
        user_id = message.from_user.id

        with salas_lock:
            if chat_id not in salas or salas[chat_id]['estado'] != 'ESPERA':
                return safe_reply(bot, message, "No hay partida en fase de espera.")
            sala = salas[chat_id]
            if len(sala['jugadores']) >= 9:
                safe_reply(bot, message, obtener_texto('join.max_players'))
                return
            if jugador_en_otra_sala(user_id, chat_id):
                safe_reply(bot, message, obtener_texto('join.already_in_other_room'))
                return
            nombre = message.from_user.first_name or message.from_user.username or f"Aspirante_{user_id}"
            sala['jugadores'][user_id] = nombre
            registrar_jugador(user_id, nombre)
            safe_reply(bot, message, formatear_texto('join.joined', player=nombre, count=len(sala['jugadores'])))
