from telebot import types
from utils.reply_helper import safe_reply
from core.db import generar_key
from core.bot import ItsukiBot
import logging

HELP_COMMANDS = [
    {"command": "/sponsor", "desc_key": "help.desc_sponsor", "sudo_level": 0, "category": "admin"}
]


HELP_COMMANDS = [
    {"command": "/sponsor", "desc_key": "help.desc_sponsor", "sudo_level": 0, "category": "admin"}
]


logger = logging.getLogger(__name__)

def register_sponsor_handlers(bot, register_command=None):
    @bot.message_handler(commands=['sponsor'])
    def sponsor_cmd(message):
        if message.chat.type != 'private':
            return safe_reply(bot, message, obtener_texto("i18n_a5e3630a"))
        user = message.from_user
        admin_channel = get_config("canal_admin")
        if not admin_channel:
            return safe_reply(bot, message, obtener_texto("i18n_sponsor_sin_canal"))
        markup = types.InlineKeyboardMarkup()
        markup.add(
            types.InlineKeyboardButton("✅ Aprobar", callback_data=f"sponsor_approve_{user.id}"),
            types.InlineKeyboardButton("❌ Rechazar", callback_data=f"sponsor_reject_{user.id}")
        )
        texto = (
            f"📩 **Solicitud de Patrocinio**\n"
            f"Usuario: {user.first_name} (ID: `{user.id}`)\n"
            f"Username: @{user.username or 'sin'}\n\n"
            "¿Autorizar la entrega de una key de activación?"
        )
        msg_queue.put(bot.send_message, admin_channel, texto, parse_mode="Markdown", reply_markup=markup)
        safe_reply(bot, message, obtener_texto("i18n_sponsor_enviada"))