"""Comandos /sizania y /testsizania – comunicados del Mainframe"""
import random, logging, psutil, time
from utils.reply_helper import safe_reply
from utils.idiomas import obtener_texto
from core.db import get_sudo_level, FRASES_GLOBALES, obtener_grupos_activos_ids

HELP_COMMANDS = [
    {"command": "/sizania", "desc_key": "help.desc_sizania", "sudo_level": 0, "category": "admin"},
    {"command": "/testsizania", "desc_key": "help.desc_testsizania", "sudo_level": 0, "category": "admin"}
]


logger = logging.getLogger(__name__)
SUDO_ADMIN = 2

def register_handlers(bot, register_command=None):
    if register_command is None:
        def register_command(name):
            def decorator(f): return f
            return decorator

    @register_command('sizania')
    def sizania_cmd(message):
        level = get_sudo_level(message.from_user.id)
        if message.chat.type in ('group', 'supergroup'):
            frase = random.choice(FRASES_GLOBALES)
            msg_queue.put(bot.send_message, message.chat.id, f'🔥 {frase}')
            return
        # privado
        if level < SUDO_ADMIN:
            return safe_reply(bot, message, obtener_texto('hardcoded.sizania_solo_grupos'))
        activos = obtener_grupos_activos_ids()
        if not activos:
            return safe_reply(bot, message, obtener_texto('hardcoded.sizania_sin_grupos'))
        frase = random.choice(FRASES_GLOBALES)
        enviados = 0
        for gid in activos:
            try:
                msg_queue.put(bot.send_message, gid, f'🔥 {frase}')
                enviados += 1
            except Exception as e:
                logger.warning(f'No se pudo enviar sizaña a {gid}: {e}')
        safe_reply(bot, message, obtener_texto('hardcoded.sizania_enviada').replace('{n}', str(enviados)))

    @register_command('testsizania')
    def testsizania_cmd(message):
        if get_sudo_level(message.from_user.id) < SUDO_ADMIN:
            return safe_reply(bot, message, obtener_texto("i18n_testsizania_acceso_denegado"))
        uptime = time.time() - psutil.Process().create_time()
        horas = int(uptime // 3600)
        minutos = int((uptime % 3600) // 60)
        frase = random.choice(FRASES_GLOBALES)
        texto = f"// [ 📢 COMUNICADO ITS ] //\n⏱️ Uptime: {horas}h {minutos}m\n\n{frase}"
        activos = obtener_grupos_activos_ids()
        if not activos:
            return safe_reply(bot, message, obtener_texto("i18n_cd471d6c"))
        for chat_id in activos:
            try:
                msg_queue.put(bot.send_message, chat_id, texto)
            except Exception as e:
                logger.warning(f"No se pudo enviar a {chat_id}: {e}")
        safe_reply(bot, message, f"✅ Sizaña enviada a {len(activos)} grupos.")