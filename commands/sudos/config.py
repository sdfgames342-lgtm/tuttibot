"""
Comandos de stickers e imágenes: /setimg, /registrarcarta, /listarcartas, /borrarcarta
"""
import telebot
from utils.idiomas import obtener_texto, formatear_texto
from utils.reply_helper import safe_reply
from utils.imagenes import guardar_imagen
from core.db import get_sudo_level, registrar_sticker, obtener_stickers, eliminar_sticker

HELP_COMMANDS = [
    {"command": "/setimg", "desc_key": "help.desc_setimg", "sudo_level": 0, "category": "admin"},
    {"command": "/registrarcarta", "desc_key": "help.desc_registrarcarta", "sudo_level": 0, "category": "admin"},
    {"command": "/listarcartas", "desc_key": "help.desc_listarcartas", "sudo_level": 0, "category": "admin"},
    {"command": "/borrarcarta", "desc_key": "help.desc_borrarcarta", "sudo_level": 0, "category": "admin"}
]


def register_handlers(bot, register_command=None):
    if register_command is None:
        def register_command(name):
            def decorator(f): return f
            return decorator

    @register_command('setimg')
    def setimg_cmd(message):
        if get_sudo_level(message.from_user.id) < 3:
            return safe_reply(bot, message, obtener_texto('setimg.denegado'))
        parts = message.text.split()
        if len(parts) < 2:
            return safe_reply(bot, message, obtener_texto('setimg.uso'))
        comando = parts[1].lower()
        if comando not in ('start', 'about', 'help', 'premium', 'montecarlo', 'banco', 'truco'):
            return safe_reply(bot, message, obtener_texto('setimg.tipo_invalido'))
        if message.reply_to_message and message.reply_to_message.photo:
            file_id = message.reply_to_message.photo[-1].file_id
        elif message.photo:
            file_id = message.photo[-1].file_id
        else:
            return safe_reply(bot, message, obtener_texto('setimg.sin_imagen'))
        guardar_imagen(comando, file_id)
        safe_reply(bot, message, formatear_texto('setimg.ok', tipo=comando))

    @register_command('registrarcarta')
    def registrarcarta_cmd(message):
        if not message.reply_to_message or not message.reply_to_message.sticker:
            return safe_reply(bot, message, obtener_texto('cards.responder_sticker'))
        parts = message.text.split()
        if len(parts) != 2:
            return safe_reply(bot, message, obtener_texto('cards.uso_registrar'))
        nombre = parts[1].strip()
        registrar_sticker(message.from_user.id, nombre, message.reply_to_message.sticker)
        safe_reply(bot, message, formatear_texto('cards.registrada', nombre=nombre))

    @register_command('listarcartas')
    def listarcartas_cmd(message):
        nombres = obtener_stickers()
        if not nombres:
            return safe_reply(bot, message, obtener_texto('cards.sin_cartas'))
        texto = obtener_texto('cards.lista') + "\n".join(f"• {n}" for n in nombres)
        safe_reply(bot, message, texto)

    @register_command('borrarcarta')
    def borrarcarta_cmd(message):
        parts = message.text.split()
        if len(parts) != 2:
            return safe_reply(bot, message, obtener_texto('cards.uso_borrar'))
        nombre = parts[1].strip()
        eliminar_sticker(nombre)
        safe_reply(bot, message, formatear_texto('cards.borrada', nombre=nombre))