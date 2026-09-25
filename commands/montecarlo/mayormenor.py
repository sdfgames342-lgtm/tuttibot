import logging
from utils.reply_helper import safe_reply

logger = logging.getLogger(__name__)

# La variable juegos_mayormenor se comparte con war.py, pero la definimos aquí también.
juegos_mayormenor = {}

HELP_COMMANDS = [
    {"command": "/mayormenor", "desc_key": "help.desc_mayormenor", "sudo_level": 0, "category": "montecarlo"}
]

def register_mayormenor_handlers(bot, register_command=None):
    @bot.message_handler(commands=['mayormenor'])
    def mayormenor_cmd(message):
        safe_reply(bot, message, "📈 Próximamente: Mayor o Menor.")
