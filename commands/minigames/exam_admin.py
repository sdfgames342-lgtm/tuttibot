import logging
from telebot import types
from core.db import set_config
from utils.idiomas import obtener_texto
from utils.reply_helper import safe_reply
from .ruleta import iniciar_ruleta, evaluar_ruleta
from .duelo import iniciar_duelo, evaluar_duelo
from .libro import evaluar_captura

HELP_COMMANDS = [
    {"command": "/exam", "desc_key": "help.desc_exam", "sudo_level": 0, "category": "admin"},
    {"command": "/duelo", "desc_key": "help.desc_duelo", "sudo_level": 0, "category": "admin"},
    {"command": "/captura", "desc_key": "help.desc_captura", "sudo_level": 0, "category": "admin"},
    {"command": "/libro", "desc_key": "help.desc_libro", "sudo_level": 0, "category": "admin"}
]


logger = logging.getLogger(__name__)

def registrar_comandos(bot, register_command, msg_queue):
    @register_command('exam')
    def exam_admin(message):
        chat_id = str(message.chat.id)
        if message.chat.type == 'private':
            return
        status = bot.get_chat_member(chat_id, message.from_user.id).status
        if status not in ['administrator', 'creator']:
            return msg_queue.put(bot.reply_to, message, obtener_texto('hardcoded.minigames_49'))
        parts = message.text.split()
        if len(parts) == 1:
            return msg_queue.put(bot.reply_to, message, obtener_texto('hardcoded.minigames_exam_config'))
        cmd = parts[1].lower()
        if cmd == 'on':
            set_config(f'exam_active_{chat_id}', '1')
            msg_queue.put(bot.reply_to, message, obtener_texto('hardcoded.minigames_51'))
        elif cmd == 'off':
            set_config(f'exam_active_{chat_id}', '0')
            msg_queue.put(bot.reply_to, message, obtener_texto('hardcoded.minigames_52'))
        elif cmd == 'time' and len(parts) > 2:
            try:
                minutos = int(parts[2])
                set_config(f'exam_interval_{chat_id}', str(minutos))
                msg_queue.put(bot.reply_to, message, obtener_texto('hardcoded.minigames_intervalo').replace('{minutos}', str(minutos)))
            except:
                msg_queue.put(bot.reply_to, message, obtener_texto('hardcoded.minigames_54'))
        else:
            msg_queue.put(bot.reply_to, message, obtener_texto('hardcoded.minigames_55'))

    @register_command('duelo')
    def duelo_cmd(message):
        parts = message.text.split()
        if len(parts) < 3:
            return msg_queue.put(bot.reply_to, message, obtener_texto('hardcoded.minigames_56'))
        try:
            apuesta = int(parts[2])
        except ValueError:
            return msg_queue.put(bot.reply_to, message, obtener_texto('hardcoded.minigames_57'))
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton('Aceptar Reto ⚔️', callback_data=f'accept_duel:{message.from_user.id}:{apuesta}'))
        msg_queue.put(bot.reply_to, message, f'⚔️ {message.from_user.first_name} ha desafiado a {parts[1]} por {apuesta} puntos!', reply_markup=markup)

    @register_command('captura')
    def captura_cmd(message):
        texto = message.text.split(maxsplit=1)
        if len(texto) < 2:
            return msg_queue.put(bot.reply_to, message, obtener_texto('hardcoded.minigames_59'))
        evaluar_captura(str(message.chat.id), message.from_user.id, texto[1], bot, msg_queue)

    @register_command('libro')
    def toggle_libro(message):
        if message.chat.type == 'private':
            return
        chat_id = str(message.chat.id)
        status = bot.get_chat_member(chat_id, message.from_user.id).status
        if status not in ['administrator', 'creator']:
            return safe_reply(bot, message, obtener_texto('hardcoded.libro_no_admin'))
        parts = message.text.split()
        if len(parts) < 2:
            return safe_reply(bot, message, obtener_texto('hardcoded.libro_uso'))
        accion = parts[1].lower()
        if accion == 'off':
            set_config(f'book_blocked_{chat_id}', '1')
            safe_reply(bot, message, obtener_texto('hardcoded.libro_bloqueado'))
        elif accion == 'on':
            set_config(f'book_blocked_{chat_id}', '0')
            safe_reply(bot, message, obtener_texto('hardcoded.libro_desbloqueado'))
        else:
            safe_reply(bot, message, obtener_texto('hardcoded.libro_accion_invalida'))