from utils.reply_helper import safe_reply
from utils.idiomas import obtener_texto
import logging

HELP_COMMANDS = [
    {"command": "/about", "desc_key": "help.desc_about", "sudo_level": 0, "category": "nodo"}
]


logger = logging.getLogger(__name__)

def register_about_handlers(bot, register_command=None):
    # Si register_command no viene, lo creamos del bot
    if register_command is None:
        def register_command(name): return bot.message_handler(commands=[name])

    @register_command('about')
    def about_cmd(message):
        texto = obtener_texto("about_main") or "<b>Itsuki Mainframe v2.0</b>"
        safe_reply(bot, message, texto, parse_mode='HTML')