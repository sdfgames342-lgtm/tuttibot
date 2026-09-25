import logging
from utils.reply_helper import safe_reply

logger = logging.getLogger(__name__)

partidas_guerra = {}    # chat_id -> datos de la partida
juegos_mayormenor = {}  # user_id -> estado, compartido por compatibilidad con salir.py

HELP_COMMANDS = [
    {"command": "/war", "desc_key": "help.desc_war", "sudo_level": 0, "category": "montecarlo"}
]

def register_war_handlers(bot, register_command=None):
    @bot.message_handler(commands=['war'])
    def war_cmd(message):
        safe_reply(bot, message, "⚔️ Próximamente: Guerra de cartas.")
