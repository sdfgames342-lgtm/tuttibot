"""
Comandos informativos: /montecarlo y /banco
Muestran imagen, descripción y botones de acceso rápido.
"""
import telebot
from utils.idiomas import obtener_texto
from utils.decorators import ItsukiLedger
from utils.reply_helper import safe_reply
from utils.imagenes import obtener_imagen

HELP_COMMANDS = [
    {"command": "/montecarlo", "desc_key": "help.desc_montecarlo", "sudo_level": 0, "category": "economia"},
    {"command": "/banco_menu", "desc_key": "help.desc_banco_menu", "sudo_level": 0, "category": "economia"}
]


HELP_COMMANDS = [
    {"command": "/montecarlo", "desc_key": "help.desc_montecarlo", "sudo_level": 0, "category": "economia"},
    {"command": "/banco_menu", "desc_key": "help.desc_banco_menu", "sudo_level": 0, "category": "economia"}
]


def register_casino_handlers(bot, register_command=None):

    @bot.message_handler(commands=['montecarlo'])
    def montecarlo_menu(message):
        uid = message.from_user.id
        msg = ItsukiLedger.render(
            title_key='montecarlo.titulo',
            body_lines=['montecarlo.cuerpo'],
            user_id=uid
        )
        markup = telebot.types.InlineKeyboardMarkup(row_width=2)
        markup.add(
            telebot.types.InlineKeyboardButton(obtener_texto('montecarlo.boton_war', user_id=uid), callback_data='cmd_war_info'),
            telebot.types.InlineKeyboardButton(obtener_texto('montecarlo.boton_mm', user_id=uid), callback_data='cmd_mm_info')
        )
        markup.add(
            telebot.types.InlineKeyboardButton(obtener_texto('montecarlo.boton_blackjack', user_id=uid), callback_data='cmd_bj_info'),
            telebot.types.InlineKeyboardButton(obtener_texto('montecarlo.boton_truco', user_id=uid), callback_data='cmd_truco_info')
        )
        markup.add(
            telebot.types.InlineKeyboardButton(obtener_texto('montecarlo.boton_apuesta', user_id=uid), callback_data='cmd_apuesta_info'),
            telebot.types.InlineKeyboardButton(obtener_texto('montecarlo.boton_itsunario', user_id=uid), callback_data='cmd_itsunario_info')
        )
        img = obtener_imagen('montecarlo')
        if img:
            safe_reply(bot, message, img, caption=msg, reply_markup=markup, parse_mode='HTML')
        else:
            safe_reply(bot, message, msg, reply_markup=markup, parse_mode='HTML')

    @bot.message_handler(commands=['banco_menu'])
    def banco_menu(message):
        uid = message.from_user.id
        msg = ItsukiLedger.render(
            title_key='banco.titulo',
            body_lines=['banco.cuerpo'],
            user_id=uid
        )
        markup = telebot.types.InlineKeyboardMarkup(row_width=1)
        markup.add(
            telebot.types.InlineKeyboardButton(obtener_texto('banco.boton_saldo', user_id=uid), callback_data='cmd_banco_saldo'),
            telebot.types.InlineKeyboardButton(obtener_texto('banco.boton_transferir', user_id=uid), callback_data='cmd_banco_transferir'),
            telebot.types.InlineKeyboardButton(obtener_texto('banco.boton_invertir', user_id=uid), callback_data='cmd_banco_invertir')
        )
        img = obtener_imagen('banco')
        if img:
            safe_reply(bot, message, img, caption=msg, reply_markup=markup, parse_mode='HTML')
        else:
            safe_reply(bot, message, msg, reply_markup=markup, parse_mode='HTML')

    # Callbacks informativos (redirigen a los comandos reales)
    @bot.callback_query_handler(func=lambda call: call.data.startswith('cmd_'))
    def casino_info_callback(call):
        data = call.data
        chat_id = call.message.chat.id
        if data == 'cmd_war_info':
            bot.send_message(chat_id, obtener_texto('montecarlo.info_war'))
        elif data == 'cmd_mm_info':
            bot.send_message(chat_id, obtener_texto('montecarlo.info_mm'))
        elif data == 'cmd_bj_info':
            bot.send_message(chat_id, obtener_texto('montecarlo.info_bj'))
        elif data == 'cmd_truco_info':
            bot.send_message(chat_id, obtener_texto('montecarlo.info_truco'))
        elif data == 'cmd_apuesta_info':
            bot.send_message(chat_id, obtener_texto('montecarlo.info_apuesta'))
        elif data == 'cmd_itsunario_info':
            bot.send_message(chat_id, obtener_texto('montecarlo.info_itsunario'))
        elif data == 'cmd_banco_saldo':
            bot.send_message(chat_id, obtener_texto('banco.info_saldo'))
        elif data == 'cmd_banco_transferir':
            bot.send_message(chat_id, obtener_texto('banco.info_transferir'))
        elif data == 'cmd_banco_invertir':
            bot.send_message(chat_id, obtener_texto('banco.info_invertir'))
        bot.answer_callback_query(call.id)