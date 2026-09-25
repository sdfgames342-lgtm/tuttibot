import logging
from utils.reply_helper import safe_reply

logger = logging.getLogger(__name__)

HELP_COMMANDS = [
    {"command": "/blackjack", "desc_key": "help.desc_blackjack", "sudo_level": 0, "category": "montecarlo"}
]

def register_blackjack_handlers(bot, register_command=None):
    @bot.message_handler(commands=['blackjack'])
    def blackjack_cmd(message):
        safe_reply(bot, message, "🃏 Próximamente: Blackjack.")
