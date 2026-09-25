"""
Comandos de usuario: /profile, /gstats, /afinidad, /start, /premium
"""
import telebot, time
import logging
from utils.idiomas import obtener_texto
from utils.message_styles import HTML_HEADER, SEPARATOR
from utils.decorators import ItsukiLedger, to_mono_font, TOP_GLOBAL_LINE, PREMIUM_MENSAJE
from utils.reply_helper import safe_reply
from core.db import (
    obtener_perfil_usuario, obtener_partidas_jugador, obtener_stats_grupo,
    obtener_partidas_grupo, obtener_jugadores_grupo, obtener_ranking_global_grupo,
    obtener_ranking_interno_grupo, obtener_puntos_usuario_en_grupo,
    obtener_puntos_grupo, obtener_afinidad, registrar_jugador, usuario_registrado
)

logger = logging.getLogger(__name__)

HELP_COMMANDS = [
    {"command": "/profile", "desc_key": "help.desc_profile", "sudo_level": 0, "category": "nodo"},
    {"command": "/gstats", "desc_key": "help.desc_gstats", "sudo_level": 0, "category": "nodo"},
    {"command": "/afinidad", "desc_key": "help.desc_afinidad", "sudo_level": 0, "category": "nodo"},
    {"command": "/start", "desc_key": "help.desc_start", "sudo_level": 0, "category": "nodo"},
    {"command": "/premium", "desc_key": "help.desc_premium", "sudo_level": 0, "category": "nodo"}
]

def _barra(porcentaje, longitud=10):
    lleno = int(porcentaje / 100.0 * longitud)
    vacio = longitud - lleno
    return '▰' * lleno + '▱' * vacio

def _progreso_rango(puntos, tipo, lang='es'):
    textos = obtener_texto(f'rankings.{tipo}', lang=lang)
    if isinstance(textos, str): return 100
    for rango in textos:
        if rango['min'] <= puntos < rango['max']:
            total = rango['max'] - rango['min']
            actual = puntos - rango['min']
            return int(actual / total * 100) if total > 0 else 100
    return 100

def _obtener_rango(puntos, tipo, lang='es'):
    textos = obtener_texto(f'rankings.{tipo}', lang=lang)
    if isinstance(textos, str): return '?'
    for rango in textos:
        if rango['min'] <= puntos < rango['max']:
            return rango.get('nombre', rango.get('nome', '?'))
    return textos[-1].get('nombre', textos[-1].get('nome', '?')) if textos else '?'

def register_handlers(bot, register_command=None, register_callback=None, msg_queue=None):
    if register_command is None:
        def register_command(name): return bot.message_handler(commands=[name])
    if register_callback is None:
        def register_callback(pattern): return bot.callback_query_handler(func=lambda call: call.data.startswith(pattern))

    @register_command('profile')
    def profile_cmd(message):
        uid = message.from_user.id
        row = obtener_perfil_usuario(uid)
        if not row:
            return safe_reply(bot, message, obtener_texto('profile.no_registrado'))
        nombre = row.get("nombre", message.from_user.first_name)
        puntos = row.get("puntos", 0)
        afinidad = row.get("afinidad", 0)
        partidas = len(obtener_partidas_jugador(uid))
        rango = _obtener_rango(puntos, 'usuario')
        ascenso_bar = _barra(_progreso_rango(puntos, 'usuario'))
        lealtad_bar = _barra(afinidad)
        msg = HTML_HEADER + '\n'
        msg += f"╭─ ⟪ {ItsukiLedger.render_solo_titulo('profile.title')} ⟫\n"
        msg += f"│ {to_mono_font(obtener_texto('profile.identidad'))}\n"
        msg += f"│ ⊛ {to_mono_font(obtener_texto('profile.nombre_label'))}: <code>{ItsukiLedger._safe(nombre)}</code>\n"
        msg += f"│ ⊛ {to_mono_font(obtener_texto('profile.alias_label'))}: @{message.from_user.username or 'sin'}\n"
        msg += f"│ ⊛ {to_mono_font(obtener_texto('profile.partidas_label'))}: <code>{partidas}</code>\n"
        msg += '│\n'
        msg += f"│ {to_mono_font(obtener_texto('profile.rendimiento'))}\n"
        msg += f"│ ⊛ {to_mono_font(obtener_texto('profile.puntos_label'))}: <code>{puntos}</code>\n"
        msg += f"│ ⊛ {to_mono_font(obtener_texto('profile.rango_label'))}: {rango}\n"
        msg += '│\n'
        msg += f"│ {to_mono_font(obtener_texto('profile.ascenso'))}\n"
        msg += f"│ {ascenso_bar} {_progreso_rango(puntos, 'usuario')}%\n"
        msg += '│\n'
        if message.chat.type in ('group', 'supergroup'):
            chat_id = str(message.chat.id)
            aportado = obtener_puntos_usuario_en_grupo(uid, chat_id)
            total_grupo = obtener_puntos_grupo(chat_id)
            pct = int(aportado / total_grupo * 100) if total_grupo > 0 else 0
            msg += f"│ {to_mono_font(obtener_texto('profile.lealtad_sector'))}\n"
            msg += f'│ {_barra(pct)} {pct}%\n'
        else:
            msg += f"│ {to_mono_font(obtener_texto('profile.lealtad'))}\n"
            msg += f'│ {lealtad_bar} {afinidad}%\n'
        msg += SEPARATOR
        safe_reply(bot, message, msg, parse_mode='HTML')

    @register_command('gstats')
    def gstats_cmd(message):
        chat_id = str(message.chat.id)
        stats = obtener_stats_grupo(chat_id)
        if not stats:
            return safe_reply(bot, message, obtener_texto('gstats.no_grupo'))
        puntos_grupo = stats.get("puntos", 0)
        usuarios = stats.get("usuarios", 0)
        partidas = len(obtener_partidas_grupo(chat_id))
        rango_grupo = _obtener_rango(puntos_grupo, 'grupo')
        ranking_global = obtener_ranking_global_grupo()
        posicion = next((i+1 for i, g in enumerate(ranking_global) if g['chat_id'] == chat_id), '-')
        pilar = obtener_ranking_interno_grupo(chat_id)
        pilar_nombre = pilar[0].get('nombre', '?') if pilar else 'N/A'
        pilar_pct = int(pilar[0].get('puntos_aportados', 0) / puntos_grupo * 100) if puntos_grupo > 0 and pilar else 0
        evolucion_bar = _barra(_progreso_rango(puntos_grupo, 'grupo'))
        msg = HTML_HEADER + '\n'
        msg += f"╭─ ⟪ {ItsukiLedger.render_solo_titulo('gstats.title')} ⟫\n"
        msg += f"│ {to_mono_font(obtener_texto('gstats.parametros'))}\n"
        msg += f"│ ⊛ {to_mono_font(obtener_texto('gstats.regentes_label'))}: <code>{usuarios}</code>\n"
        msg += f"│ ⊛ {to_mono_font(obtener_texto('profile.puntos_label'))}: <code>{puntos_grupo}</code>\n"
        msg += f"│ ⊛ {to_mono_font(obtener_texto('profile.partidas_label'))}: <code>{partidas}</code>\n"
        msg += f"│ ⊛ {to_mono_font(obtener_texto('profile.rango_label'))}: {rango_grupo}\n"
        msg += TOP_GLOBAL_LINE.format(pos=posicion) + '\n'
        msg += f"│ {to_mono_font(obtener_texto('gstats.evolucion'))}\n"
        msg += f"│ {evolucion_bar} {_progreso_rango(puntos_grupo, 'grupo')}%\n"
        msg += f"│ {to_mono_font(obtener_texto('gstats.pilar_central'))}\n"
        msg += f"│ ⊛ {to_mono_font(obtener_texto('gstats.alfa_label'))}: <code>{ItsukiLedger._safe(pilar_nombre)}</code>\n"
        msg += f'│ {_barra(pilar_pct)} {pilar_pct}%\n'
        msg += SEPARATOR
        safe_reply(bot, message, msg, parse_mode='HTML')

    @register_command('afinidad')
    def afinidad_cmd(message):
        uid = message.reply_to_message.from_user.id if message.reply_to_message else message.from_user.id
        nivel = obtener_afinidad(uid)
        if nivel >= 80: emoji, comentario = '🌸', obtener_texto('profile.afinidad_alta')
        elif nivel >= 50: emoji, comentario = '📊', obtener_texto('profile.afinidad_media')
        elif nivel >= 20: emoji, comentario = '🔍', obtener_texto('profile.afinidad_baja')
        else: emoji, comentario = '💤', obtener_texto('profile.afinidad_minima')
        safe_reply(bot, message, f'{emoji} {obtener_texto("profile.afinidad")}: {nivel}/100\n\n{comentario}')

    @register_command('start')
    def start_cmd(message):
        uid = message.from_user.id
        if message.chat.type in ('group', 'supergroup'):
            markup = telebot.types.InlineKeyboardMarkup()
            bot_username = bot.get_me().username
            markup.add(telebot.types.InlineKeyboardButton(
                obtener_texto('start.boton_privado'),
                url=f'https://t.me/{bot_username}?start=register'))
            safe_reply(bot, message, obtener_texto('hardcoded.start_registro_privado'), reply_markup=markup)
            return
        if usuario_registrado(uid):
            row = obtener_perfil_usuario(uid)
            nombre = row.get("nombre", message.from_user.first_name) if row else message.from_user.first_name
            msg = ItsukiLedger.render(
                title_key='start.rebienvenida_titulo',
                body_lines=['start.rebienvenida_cuerpo'],
                variables={obtener_texto('profile.nombre_label'): nombre},
                user_id=uid)
            markup = telebot.types.InlineKeyboardMarkup(row_width=2)
            markup.add(telebot.types.InlineKeyboardButton(obtener_texto('start.boton_help'), callback_data='show_help'),
                       telebot.types.InlineKeyboardButton(obtener_texto('start.boton_about'), callback_data='show_about'))
            markup.add(telebot.types.InlineKeyboardButton(obtener_texto('start.boton_profile'), callback_data='show_profile'))
            safe_reply(bot, message, msg, reply_markup=markup, parse_mode='HTML')
            return
        markup = telebot.types.InlineKeyboardMarkup()
        markup.add(telebot.types.InlineKeyboardButton(obtener_texto('legal.register_btn'),
                      callback_data=f'legal_start_{uid}'))
        msg = HTML_HEADER + '\n'
        msg += f"╭─ ⟪ {ItsukiLedger.render_solo_titulo('start.welcome')} ⟫\n"
        msg += f"│ {obtener_texto('legal.user_start')}\n"
        msg += SEPARATOR
        safe_reply(bot, message, msg, reply_markup=markup, parse_mode='HTML')

    @register_callback('legal_start_')
    def legal_start_callback(call):
        uid = int(call.data.replace('legal_start_', ''))
        if not usuario_registrado(uid):
            registrar_jugador(uid, call.from_user.first_name)
        row = obtener_perfil_usuario(uid)
        nombre = row.get("nombre", call.from_user.first_name) if row else call.from_user.first_name
        msg = ItsukiLedger.render(
            title_key='start.bienvenida_titulo',
            body_lines=['start.bienvenida_cuerpo'],
            variables={obtener_texto('profile.nombre_label'): nombre},
            user_id=uid)
        markup = telebot.types.InlineKeyboardMarkup(row_width=2)
        markup.add(telebot.types.InlineKeyboardButton(obtener_texto('start.boton_help'), callback_data='show_help'),
                   telebot.types.InlineKeyboardButton(obtener_texto('start.boton_about'), callback_data='show_about'))
        markup.add(telebot.types.InlineKeyboardButton(obtener_texto('start.boton_profile'), callback_data='show_profile'))
        markup.add(telebot.types.InlineKeyboardButton(obtener_texto('start.boton_crear'), callback_data='goto_create_info'))
        safe_reply(bot, call.message, msg, reply_markup=markup, parse_mode='HTML')
        try: bot.delete_message(call.message.chat.id, call.message.message_id)
        except: pass
        bot.answer_callback_query(call.id)

    @register_callback('show_help')
    def show_help_cb(call): safe_reply(bot, call.message, obtener_texto('start.help')); bot.answer_callback_query(call.id)
    @register_callback('show_about')
    def show_about_cb(call): safe_reply(bot, call.message, obtener_texto('start.about')); bot.answer_callback_query(call.id)
    @register_callback('show_start')
    def show_start_cb(call): safe_reply(bot, call.message, obtener_texto('start.welcome')); bot.answer_callback_query(call.id)
    @register_callback('goto_create_info')
    def goto_create_info_cb(call): safe_reply(bot, call.message, obtener_texto('start.create_info')); bot.answer_callback_query(call.id)

    @register_command('premium')
    def premium_cmd(message):
        markup = telebot.types.InlineKeyboardMarkup()
        markup.add(telebot.types.InlineKeyboardButton('💎 Solicitar Acceso al Núcleo', callback_data='interest_premium'))
        safe_reply(bot, message, PREMIUM_MENSAJE, reply_markup=markup, parse_mode='Markdown')

    @bot.callback_query_handler(func=lambda call: call.data == 'interest_premium')
    def premium_callback(call):
        user_id = call.from_user.id
        username = call.from_user.username or 'Anónimo'
        nombre = call.from_user.first_name or 'Desconocido'
        with open('interesados_premium.log', 'a') as f:
            f.write(f"{time.strftime('%Y-%m-%d %H:%M:%S')} | ID: {user_id} | @{username} | {nombre}\n")
        logger.info(f'Interés premium registrado: {user_id} (@{username})')
        bot.answer_callback_query(call.id, obtener_texto("i18n_premium_registrada"))
