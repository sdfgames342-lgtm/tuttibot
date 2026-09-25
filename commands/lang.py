"""
Comando /lang – Cambia el idioma del chat (grupo) o usuario (privado).
"""
from utils.idiomas import obtener_texto, formatear_texto, establecer_idioma_chat, establecer_idioma_usuario, IDIOMAS
from utils.reply_helper import safe_reply

HELP_COMMANDS = [
    {"command": "/lang", "desc_key": "help.desc_lang", "sudo_level": 0, "category": "nodo"}
]


def register_handlers(bot, register_command=None):
    if register_command is None:
        def register_command(name):
            def decorator(f): return f
            return decorator

    @register_command('lang')
    def lang_cmd(message):
        parts = message.text.split()
        if len(parts) < 2:
            return safe_reply(bot, message, obtener_texto('lang.usage', chat_id=str(message.chat.id)))
        lang = parts[1].lower()
        if lang not in IDIOMAS:
            idiomas_disponibles = ', '.join(IDIOMAS.keys())
            return safe_reply(bot, message, formatear_texto('lang.invalid', chat_id=str(message.chat.id), idiomas=idiomas_disponibles))
        if message.chat.type in ('group', 'supergroup'):
            try:
                member = bot.get_chat_member(message.chat.id, message.from_user.id)
                if member.status not in ('administrator', 'creator'):
                    return safe_reply(bot, message, obtener_texto('panel.solo_admin_idioma'))
            except:
                return safe_reply(bot, message, obtener_texto('panel.no_verificar'))
        if message.chat.type == 'private':
            establecer_idioma_usuario(message.from_user.id, lang)
            safe_reply(bot, message, formatear_texto('lang.set_user', lang=lang))
        else:
            establecer_idioma_chat(str(message.chat.id), lang)
            safe_reply(bot, message, formatear_texto('lang.set_chat', lang=lang))