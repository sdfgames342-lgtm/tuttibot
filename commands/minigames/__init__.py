"""
Paquete de minijuegos. Cada submódulo maneja un sistema de juego.
"""
import logging, threading
from telebot import types

from core.db import obtener_libro_capturable, get_config, contar_grupos_activos
from utils.idiomas import obtener_texto
from utils.reply_helper import safe_reply

from ._reaper import iniciar_reaper
from .ruleta import iniciar_ruleta, evaluar_ruleta
from .duelo import iniciar_duelo, evaluar_duelo
from .libro import viajar_libro, evaluar_captura
from .exam_admin import registrar_comandos

logger = logging.getLogger(__name__)

def registrar_minigames(bot, register_command, msg_queue):
    # Iniciar hilos de limpieza y libro viajero (solo una vez)
    iniciar_reaper(bot, msg_queue)
    threading.Thread(target=viajar_libro, args=(bot, msg_queue), daemon=True).start()

    # Registrar comandos administrativos y de juego
    registrar_comandos(bot, register_command, msg_queue)

    # Handler automático de texto (evalúa ruleta/duelo en grupos)
    @bot.message_handler(func=lambda m: m.text and m.chat.type in ('group', 'supergroup'))
    def evaluar_minigames(message):
        if message.text.strip().startswith('/'):
            return
        chat_id = str(message.chat.id)
        texto = message.text.strip()
        evaluar_ruleta(chat_id, message.from_user.id, texto, bot, msg_queue)
        evaluar_duelo(chat_id, message.from_user.id, texto, bot, msg_queue)

    # Callback para abrir libro
    @bot.callback_query_handler(func=lambda call: call.data.startswith('open_book:'))
    def abrir_libro_callback(call):
        libro_id = int(call.data.split(':')[1])
        cap = obtener_libro_capturable(call.message.chat.id)
        if cap:
            bot.answer_callback_query(call.id, obtener_texto('hardcoded.minigames_60'))
            msg_text = obtener_texto('hardcoded.pregunta_tomo').replace('{pregunta}', cap[1])
            msg_queue.put(bot.send_message, call.message.chat.id, msg_text)
        else:
            bot.answer_callback_query(call.id, obtener_texto('hardcoded.minigames_62'))

    # Callback para aceptar duelo
    @bot.callback_query_handler(func=lambda call: call.data.startswith('accept_duel:'))
    def aceptar_duelo_callback(call):
        bot.answer_callback_query(call.id, obtener_texto('hardcoded.minigames_63'))
        chat_id = str(call.message.chat.id)
        iniciar_duelo(chat_id, bot, msg_queue)

    # Callback de lista de espera
    @bot.callback_query_handler(func=lambda call: call.data == 'waiting_list_info')
    def waiting_list_callback(call):
        bot.answer_callback_query(call.id, obtener_texto('hardcoded.minigames_65'), show_alert=True)
