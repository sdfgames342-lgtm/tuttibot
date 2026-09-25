import telebot
from utils.idiomas import obtener_texto
from utils.decorators import ItsukiLedger, to_mono_font
from core.help_generator import generar_menu
from core.db import get_sudo_level
from core.help_generator import SUDO_MOD
from utils.reply_helper import safe_reply

HELP_COMMANDS = [
    {"command": "/help", "desc_key": "help.desc_help", "sudo_level": 0, "category": "nodo"},
    {"command": "/shelp", "desc_key": "help.desc_shelp", "sudo_level": 0, "category": "nodo"}
]


def register_handlers(bot, register_command=None):
    if register_command is None:
        def register_command(name):
            def decorator(f): return f
            return decorator

    @register_command('help')
    def help_cmd(message):
        uid = message.from_user.id
        cats = generar_menu(uid)
        from utils.imagenes import obtener_imagen
        img = obtener_imagen('help')
        markup = telebot.types.InlineKeyboardMarkup(row_width=2)
        for cat_key, cat_info in cats.items():
            markup.add(telebot.types.InlineKeyboardButton(
                f"{cat_info['emoji']} {cat_info['label']}",
                callback_data=f'help_cat_{cat_key}'))
        markup.add(telebot.types.InlineKeyboardButton('❌ Cerrar', callback_data='help_cat_cerrar'))
        titulo = obtener_texto('help.titulo_principal')
        if img:
            try:
                safe_reply(bot, message, img, caption=titulo, reply_markup=markup, parse_mode='HTML')
                return
            except:
                pass
        safe_reply(bot, message, titulo, reply_markup=markup, parse_mode='HTML')

    @bot.callback_query_handler(func=lambda call: call.data.startswith('help_cat_'))
    def help_category_callback(call):
        data = call.data
        chat_id = call.message.chat.id
        message_id = call.message.message_id
        uid = call.from_user.id

        if data == 'help_cat_cerrar':
            try:
                bot.delete_message(chat_id, message_id)
            except:
                pass
            return

        cat_key = data.replace('help_cat_', '')
        if cat_key == 'volver':
            # Regenerar menú principal
            cats = generar_menu(uid)
            markup = telebot.types.InlineKeyboardMarkup(row_width=2)
            for ck, ci in cats.items():
                markup.add(telebot.types.InlineKeyboardButton(
                    f"{ci['emoji']} {ci['label']}",
                    callback_data=f'help_cat_{ck}'))
            markup.add(telebot.types.InlineKeyboardButton('❌ Cerrar', callback_data='help_cat_cerrar'))
            titulo = obtener_texto('help.titulo_principal')
            try:
                if call.message.content_type == 'photo':
                    bot.edit_message_caption(chat_id=chat_id, message_id=message_id, caption=titulo, reply_markup=markup)
                else:
                    bot.edit_message_text(titulo, chat_id, message_id, reply_markup=markup)
            except:
                bot.answer_callback_query(call.id, obtener_texto("str_fadd90d4"))
            return

        # Categoría específica
        cats = generar_menu(uid)
        if cat_key not in cats:
            bot.answer_callback_query(call.id)
            return

        cat_info = cats[cat_key]
        texto = f"{cat_info['emoji']} **{cat_info['label']}**\n"
        for cmd in cat_info['comandos']:
            texto += f"│ {cmd}\n"
        markup = telebot.types.InlineKeyboardMarkup()
        markup.add(
            telebot.types.InlineKeyboardButton('🔙 Volver', callback_data='help_cat_volver'),
            telebot.types.InlineKeyboardButton('❌ Cerrar', callback_data='help_cat_cerrar'))
        try:
            if call.message.content_type == 'photo':
                bot.edit_message_caption(chat_id=chat_id, message_id=message_id, caption=texto, reply_markup=markup, parse_mode='Markdown')
            else:
                bot.edit_message_text(texto, chat_id, message_id, reply_markup=markup, parse_mode='Markdown')
        except:
            bot.answer_callback_query(call.id, obtener_texto("str_fadd90d4"))
        bot.answer_callback_query(call.id)

    @register_command('shelp')
    def shelp_cmd(message):
        if get_sudo_level(message.from_user.id) < SUDO_MOD:
            return safe_reply(bot, message, obtener_texto("str_5208d289"))
        # Redirigir al help dinámico (ya filtra automáticamente)
        help_cmd(message)