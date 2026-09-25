import random, time, threading, logging
from telebot import types
from core.db import (
    get_connection, get_config, set_config, contar_grupos_activos,
    obtener_pregunta_biblioteca, obtener_grupo_aleatorio_activo,
    asignar_libro, obtener_libro_capturable, capturar_libro, sumar_puntos_grupo
)
from utils.idiomas import obtener_texto
from utils.reply_helper import safe_reply

logger = logging.getLogger(__name__)

def viajar_libro(bot, msg_queue):
    bot_username = bot.get_me().username
    while True:
        time.sleep(random.randint(10800, 21600))
        for lang in ['es', 'pt']:
            try:
                libro = obtener_pregunta_biblioteca(lang)
                if not libro:
                    continue
                libro_id, titulo, pregunta, resp = libro
                chat_id = obtener_grupo_aleatorio_activo()
                if not chat_id:
                    continue
                asignar_libro(libro_id, chat_id)
                markup = types.InlineKeyboardMarkup()
                texto_btn = '🔓 Abrir Tomo' if lang == 'es' else '🔓 Abrir Livro'
                markup.add(types.InlineKeyboardButton(texto_btn, callback_data=f'open_book:{libro_id}'))
                if contar_grupos_activos() < 100:
                    markup.add(types.InlineKeyboardButton('➕ Invitar bot a tu grupo', url=f'https://t.me/{bot_username}?startgroup=true'))
                else:
                    markup.add(types.InlineKeyboardButton('🟡 Lista de espera activa', callback_data='waiting_list_info'))
                msg_text = obtener_texto('hardcoded.minigames_libro_evento').replace('{titulo}', titulo)
                msg_queue.put(bot.send_message, chat_id, msg_text, reply_markup=markup)
                canal = get_config('canal_marketing')
                if canal:
                    markup_canal = types.InlineKeyboardMarkup()
                    if contar_grupos_activos() < 100:
                        markup_canal.add(types.InlineKeyboardButton('➕ Invitar bot a tu grupo', url=f'https://t.me/{bot_username}?startgroup=true'))
                    msg_canal = obtener_texto('hardcoded.minigames_libro_canal').replace('{titulo}', titulo).replace('{chat_id}', chat_id)
                    msg_queue.put(bot.send_message, canal, msg_canal, reply_markup=markup_canal)
            except Exception as e:
                logger.error(f'viajar_libro: {e}')

def evaluar_captura(chat_id, user_id, texto, bot, msg_queue):
    cap = obtener_libro_capturable(chat_id)
    if not cap:
        return
    libro_id, resp, titulo = cap
    if texto.strip().lower() != resp.lower():
        msg_queue.put(bot.send_message, chat_id, obtener_texto('hardcoded.minigames_46'))
        return

    def animar():
        m = safe_reply(bot, None, obtener_texto('hardcoded.minigames_captura_animando'))
        for f in ['📕', '📙', '📒', '📖', '✨']:
            time.sleep(0.4)
            try:
                bot.edit_message_text(f' {f} [EXTRAYENDO: {titulo}]', chat_id, m.message_id)
            except:
                pass
        final_msg = obtener_texto('hardcoded.minigames_captura_ganada').replace('{user_id}', str(user_id)).replace('{titulo}', titulo)
        bot.edit_message_text(final_msg, chat_id, m.message_id)
    threading.Thread(target=animar, daemon=True).start()
    capturar_libro(libro_id, user_id, chat_id)
    sumar_puntos_grupo(chat_id, 1500)
    canal = get_config('canal_marketing')
    if canal:
        msg_queue.put(bot.send_message, canal, f"📚 El grupo {chat_id} ha capturado '{titulo}'.")
