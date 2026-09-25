import logging
from utils.reply_helper import safe_reply

logger = logging.getLogger(__name__)

HELP_COMMANDS = [
    {"command": "/apuesta", "desc_key": "help.desc_apuesta", "sudo_level": 0, "category": "montecarlo"}
]

def register_apuesta_handlers(bot, register_command=None):
    @bot.message_handler(commands=['apuesta'])
    def apuesta_cmd(message):
        safe_reply(bot, message, "🎲 Próximamente: Apuesta de cartas contra el bot.")
