"""
Comandos /cagon y /off – ahora agnósticos usando game_core.
"""
from utils.reply_helper import safe_reply
from utils.idiomas import obtener_texto
from game_core.registry import get_game, unregister_game
import logging

logger = logging.getLogger(__name__)

HELP_COMMANDS = [
    {"command": "/cagon", "desc_key": "help.desc_cagon", "sudo_level": 0, "category": "juegos"},
    {"command": "/off", "desc_key": "help.desc_off", "sudo_level": 0, "category": "juegos"}
]

def register_salir_handlers(bot, register_command=None, salas=None, salas_lock=None):

    @bot.message_handler(commands=['cagon'])
    def cagon_cmd(message):
        chat_id = str(message.chat.id)
        user_id = message.from_user.id
        game = get_game(chat_id)
        if game:
            return game.abandon(user_id)
        # Si no hay juego nuevo, intentar Tutti‑Frutti (legado)
        if salas and chat_id in salas:
            sala = salas[chat_id]
            if sala.get('estado') == 'ESPERA':
                if user_id == sala.get('creador'):
                    del salas[chat_id]
                    return safe_reply(bot, message, obtener_texto("i18n_cagon_creador"))
                if user_id in sala.get('jugadores', {}):
                    sala['jugadores'].pop(user_id)
                    return safe_reply(bot, message, f"{user_id} abandonó la sala")
            return safe_reply(bot, message, obtener_texto("i18n_3b09b637"))
        return safe_reply(bot, message, "No estás en ninguna partida activa.")

    @bot.message_handler(commands=['off'])
    def off_cmd(message):
        chat_id = str(message.chat.id)
        user_id = message.from_user.id
        game = get_game(chat_id)
        if game:
            return game.cancel(user_id)
        # Tutti‑Frutti legado
        if salas and chat_id in salas:
            sala = salas[chat_id]
            if user_id == sala.get('creador'):
                del salas[chat_id]
                return safe_reply(bot, message, obtener_texto("i18n_afc3fe94"))
            return safe_reply(bot, message, obtener_texto("i18n_35105b38"))
        return safe_reply(bot, message, "No hay partida activa que cancelar.")
