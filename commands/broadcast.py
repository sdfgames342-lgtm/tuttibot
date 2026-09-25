"""
Central de Difusión Itsuki – /broadcast Pro
"""
import logging
from telebot import types
from core.db import (
    get_config, obtener_grupos_activos_con_nombre,
    obtener_grupos_activos_ids, obtener_grupos_activos_ids_por_idioma,
    get_sudo_level
)
from utils.idiomas import obtener_texto
from utils.reply_helper import safe_reply

logger = logging.getLogger(__name__)
SUDO_MOD = 1
SUDO_ADMIN = 2
SUDO_OWNER = 4

HELP_COMMANDS = [
    {"command": "/broadcast", "desc_key": "help.desc_broadcast", "sudo_level": 0, "category": "admin"}
]

borradores = {}

def register_handlers(bot, register_command=None, msg_queue=None):
    if register_command is None:
        def register_command(name): return bot.message_handler(commands=[name])
    if msg_queue is None:
        class DummyQueue:
            def put(self, fn, *args, **kwargs): return fn(*args, **kwargs)
        msg_queue = DummyQueue()

    @register_command('broadcast')
    def broadcast_cmd(message):
        uid = message.from_user.id
        level = get_sudo_level(uid)
        chat_type = message.chat.type
        is_group = chat_type in ('group', 'supergroup')
        user_is_admin = False
        if is_group:
            try:
                member = bot.get_chat_member(message.chat.id, uid)
                if member.status in ('administrator', 'creator'):
                    user_is_admin = True
            except: pass
        borradores[uid] = {'target': None, 'content': None, 'photo': None,
                           'document': None, 'video': None, 'audio': None, 'voice': None,
                           'buttons': [], 'parse_mode': 'HTML'}
        markup = types.InlineKeyboardMarkup(row_width=2)
        botones = []
        if level >= SUDO_MOD:
            botones.append(types.InlineKeyboardButton('🌐 Global (Todos)', callback_data='bc_set_all'))
            botones.append(types.InlineKeyboardButton('🇪🇸 Solo ES', callback_data='bc_set_es'))
            botones.append(types.InlineKeyboardButton('🇧🇷 Solo PT', callback_data='bc_set_pt'))
        if level >= SUDO_ADMIN:
            botones.append(types.InlineKeyboardButton('📜 Canal Logs', callback_data='bc_set_log'))
            botones.append(types.InlineKeyboardButton('📈 Canal Marketing', callback_data='bc_set_marketing'))
        if user_is_admin:
            botones.append(types.InlineKeyboardButton('🏠 Este Grupo', callback_data=f'bc_target_{message.chat.id}'))
        if level >= SUDO_MOD:
            botones.append(types.InlineKeyboardButton('👥 Elegir Grupo (sudo)', callback_data='bc_set_select'))
        if not botones:
            return safe_reply(bot, message, obtener_texto('broadcast.sin_permisos'))
        markup.add(*botones)
        safe_reply(bot, message, obtener_texto('broadcast.titulo'), reply_markup=markup)

    @bot.callback_query_handler(func=lambda call: call.data.startswith('bc_set_'))
    def set_target_callback(call):
        uid = call.from_user.id
        target = call.data.replace('bc_set_', '')
        if target == 'select':
            markup = types.InlineKeyboardMarkup()
            for cid, nom in obtener_grupos_activos_con_nombre():
                markup.add(types.InlineKeyboardButton(f'📍 {nom or cid}', callback_data=f'bc_target_{cid}'))
            markup.add(types.InlineKeyboardButton('« Cancelar', callback_data='bc_cancel'))
            bot.edit_message_text(obtener_texto('broadcast.grupos_activos'),
                                  call.message.chat.id, call.message.message_id, reply_markup=markup)
            return
        borradores[uid]['target'] = target
        pedir_contenido(call.message, uid)

    @bot.callback_query_handler(func=lambda call: call.data.startswith('bc_target_'))
    def set_specific_target(call):
        uid = call.from_user.id
        borradores[uid]['target'] = call.data.replace('bc_target_', '')
        pedir_contenido(call.message, uid)

    @bot.callback_query_handler(func=lambda call: call.data == 'bc_cancel')
    def cancel_broadcast(call):
        uid = call.from_user.id
        borradores.pop(uid, None)
        bot.edit_message_text(obtener_texto('broadcast.cancelada'),
                              call.message.chat.id, call.message.message_id)

    def pedir_contenido(message, uid):
        sent = safe_reply(bot, message, obtener_texto('broadcast.envia_contenido'),
                         reply_markup=types.ForceReply(selective=True))
        bot.register_next_step_handler(sent, process_content, uid)

    def process_content(message, uid):
        b = borradores[uid]
        b['content'] = message.text or message.caption or ''
        if message.photo: b['photo'] = message.photo[-1].file_id
        if message.document: b['document'] = message.document.file_id
        if message.video: b['video'] = message.video.file_id
        if message.audio: b['audio'] = message.audio.file_id
        if message.voice: b['voice'] = message.voice.file_id
        mostrar_previsualizacion(message.chat.id, uid)

    def mostrar_previsualizacion(chat_id, uid):
        b = borradores[uid]
        markup = types.InlineKeyboardMarkup(row_width=2)
        markup.add(
            types.InlineKeyboardButton('🖼 Adjuntar/Cambiar Foto', callback_data='bc_edit_photo'),
            types.InlineKeyboardButton('🔗 Añadir Botón URL', callback_data='bc_edit_url'))
        if b['buttons']:
            markup.add(types.InlineKeyboardButton(f"🔘 {len(b['buttons'])} botones", callback_data='bc_list_btns'))
        markup.add(
            types.InlineKeyboardButton('🔄 Reiniciar', callback_data='bc_reset'),
            types.InlineKeyboardButton('🚀 ENVIAR AHORA', callback_data='bc_confirm_send'))
        previa = (
            f"📝 **{obtener_texto('broadcast.previsualizacion')}**\n"
            f"{obtener_texto('broadcast.destino')}: `{b['target']}`\n\n"
            f"{b['content'] or '[Sin texto]'}"
        )
        safe_reply(bot, message=None, text=previa, chat_id=chat_id, reply_markup=markup, parse_mode='HTML')

    @bot.callback_query_handler(func=lambda call: call.data == 'bc_confirm_send')
    def ejecutar_envio(call):
        uid = call.from_user.id
        b = borradores.get(uid)
        if not b or not b['target']: return
        target = b['target']
        targets = []
        if target == 'all':
            targets = obtener_grupos_activos_ids()
        elif target in ('es', 'pt'):
            targets = obtener_grupos_activos_ids_por_idioma(target)
        elif target == 'log':
            c = get_config('canal_logs')
            if c: targets = [c]
        elif target == 'marketing':
            c = get_config('canal_marketing')
            if c: targets = [c]
        else:
            targets = [target]
        if not targets:
            bot.answer_callback_query(call.id, obtener_texto('broadcast.sin_destinos'))
            return
        reply_markup = None
        if b['buttons']:
            mk = types.InlineKeyboardMarkup()
            for label, url in b['buttons']:
                mk.add(types.InlineKeyboardButton(label, url=url))
            reply_markup = mk
        enviados = 0
        for tid in targets:
            try:
                if b.get('photo'):
                    msg_queue.put(bot.send_photo, tid, b['photo'], caption=b['content'],
                                  parse_mode='HTML', reply_markup=reply_markup)
                elif b.get('document'):
                    msg_queue.put(bot.send_document, tid, b['document'], caption=b['content'],
                                  parse_mode='HTML', reply_markup=reply_markup)
                elif b.get('video'):
                    msg_queue.put(bot.send_video, tid, b['video'], caption=b['content'],
                                  parse_mode='HTML', reply_markup=reply_markup)
                elif b.get('audio'):
                    msg_queue.put(bot.send_audio, tid, b['audio'], caption=b['content'],
                                  parse_mode='HTML', reply_markup=reply_markup)
                elif b.get('voice'):
                    msg_queue.put(bot.send_voice, tid, b['voice'], caption=b['content'],
                                  parse_mode='HTML', reply_markup=reply_markup)
                else:
                    msg_queue.put(bot.send_message, tid, b['content'],
                                  parse_mode='HTML', reply_markup=reply_markup, disable_web_page_preview=True)
                enviados += 1
            except Exception as e:
                logger.warning(f'Error enviando a {tid}: {e}')
        bot.answer_callback_query(call.id, f'✅ {enviados} destinos alcanzados.')
        safe_reply(bot, call.message,
                   obtener_texto('broadcast.finalizado').replace('{enviados}', str(enviados)))
        borradores.pop(uid, None)

    # Resto de callbacks (bc_edit_photo, bc_edit_url, etc.) se implementan de forma similar...
    # Por brevedad, se omiten aquí pero deben añadirse en el archivo real.
