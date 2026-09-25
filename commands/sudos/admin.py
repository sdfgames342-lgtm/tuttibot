import os, logging, time
from telebot import types
from utils.reply_helper import safe_reply
from utils.idiomas import obtener_texto
from utils.decorators import ItsukiLedger
from core.db import (
    get_sudo_level, set_sudo_level,
    get_config, set_config, delete_config,
    contar_grupos_activos, desactivar_grupo, activar_grupo, registrar_grupo,
    grupo_activo, generar_key, validar_key,
    obtener_ultimo_grupo_activo, obtener_todos_chat_ids, eliminar_grupo_por_id,
    obtener_ids_sin_nombre, actualizar_nombre_grupo, obtener_grupos_paginados,
    contar_todos_grupos, get_connection
)

HELP_COMMANDS = [
    {"command": "/activar", "desc_key": "help.desc_activar", "sudo_level": 0, "category": "admin"},
    {"command": "/sudo", "desc_key": "help.desc_sudo", "sudo_level": 4, "category": "admin"},
    {"command": "/genkey", "desc_key": "help.desc_genkey", "sudo_level": 4, "category": "admin"},
    {"command": "/otorgar_inicial", "desc_key": "help.desc_otorgar_inicial", "sudo_level": 4, "category": "admin"},
    {"command": "/canal_marketing", "desc_key": "help.desc_canal_marketing", "sudo_level": 3, "category": "admin"},
    {"command": "/canal_logs", "desc_key": "help.desc_canal_logs", "sudo_level": 3, "category": "admin"},
    {"command": "/canal_admin", "desc_key": "help.desc_canal_admin", "sudo_level": 3, "category": "admin"},
    {"command": "/groups", "desc_key": "help.desc_groups", "sudo_level": 2, "category": "admin"},
    {"command": "/kick_sector", "desc_key": "help.desc_kick_sector", "sudo_level": 2, "category": "admin"},
    {"command": "/ban_user", "desc_key": "help.desc_ban_user", "sudo_level": 3, "category": "admin"},
    {"command": "/verificar_grupos", "desc_key": "help.desc_verificar_grupos", "sudo_level": 2, "category": "admin"},
    {"command": "/cleanup_salas", "desc_key": "help.desc_cleanup_salas", "sudo_level": 2, "category": "admin"},
    {"command": "/analityc", "desc_key": "help.desc_analityc", "sudo_level": 2, "category": "admin"}
]






logger = logging.getLogger(__name__)

SUDO_OWNER = 4
SUDO_COOWNER = 3
SUDO_ADMIN = 2
SUDO_MOD = 1

MENSAJE_PERMISO = "admin.permiso_denegado"

def check_sudo(message, level, bot):
    """Verifica si el usuario tiene el nivel de sudo requerido. Responde con i18n si no."""
    user_id = message.from_user.id
    user_level = get_sudo_level(user_id)
    if user_level < level:
        safe_reply(bot, message, obtener_texto(MENSAJE_PERMISO, user_id=user_id))
        return False
    return True

# Almacén temporal para el proceso de activación con clave
pending_activations = {}

def register_admin_handlers(bot, register_command=None, msg_queue=None, salas=None, salas_lock=None):
    """
    Registra todos los comandos administrativos y de activación.
    salas y salas_lock solo se usan para /cleanup_salas; si vienen None se omite esa función.
    """

    # ─── COMANDOS PÚBLICOS (sin restricción de nivel) ───

    @bot.message_handler(commands=['activar'])
    def activar_cmd(message):
        if message.chat.type == 'private':
            return safe_reply(bot, message, obtener_texto("i18n_activar_solo_grupo"))
        parts = message.text.split()
        if len(parts) != 2:
            return safe_reply(bot, message, obtener_texto("i18n_2e71d37f"))
        key = parts[1].strip()
        chat_id = str(message.chat.id)
        if validar_key(key):
            nombre = getattr(message.chat, 'title', str(chat_id))
            pending_activations[chat_id] = {'nombre': nombre, 'activado': False, 'key': key}
            markup = types.InlineKeyboardMarkup()
            markup.add(
                types.InlineKeyboardButton(
                    obtener_texto("legal.accept_btn"),
                    callback_data=f"legal_accept_{chat_id}"
                )
            )
            safe_reply(bot, message, obtener_texto("legal.key_activation"), reply_markup=markup, parse_mode='HTML')
        else:
            safe_reply(bot, message, obtener_texto("i18n_activar_key_invalida"))

    # Callback para aceptar términos y activar el grupo
    @bot.callback_query_handler(func=lambda call: call.data.startswith('legal_accept_'))
    def legal_callback(call):
        chat_id = call.data.replace('legal_accept_', '')
        if chat_id not in pending_activations:
            return bot.answer_callback_query(call.id, "Solicitud expirada.")
        info = pending_activations.pop(chat_id)
        registrar_grupo(chat_id, info['nombre'])
        activar_grupo(chat_id)
        bot.answer_callback_query(call.id, "✅ Grupo activado.")
        safe_reply(bot, call.message, obtener_texto("i18n_activar_grupo_ok"))

    # ─── COMANDOS RESTRINGIDOS ───

    @bot.message_handler(commands=['sudo'])
    def sudo_cmd(message):
        if not check_sudo(message, SUDO_OWNER, bot):
            return
        parts = message.text.split()
        if len(parts) != 3:
            return safe_reply(bot, message, obtener_texto("admin.sudo_uso"))
        try:
            target_user = int(parts[1])
            level = int(parts[2])
            if level < 0 or level > 4:
                raise ValueError
        except ValueError:
            return safe_reply(bot, message, obtener_texto("admin.sudo_uso"))
        set_sudo_level(target_user, level)
        safe_reply(bot, message, obtener_texto("admin.sudo_ok").replace('{uid}', str(target_user)).replace('{level}', str(level)))

    @bot.message_handler(commands=['genkey'])
    def genkey_cmd(message):
        if not check_sudo(message, SUDO_OWNER, bot):
            return
        key = generar_key("standard")
        safe_reply(bot, message, obtener_texto("admin.genkey_ok").replace('{key}', key), parse_mode='HTML')

    @bot.message_handler(commands=['otorgar_inicial'])
    def otorgar_inicial_cmd(message):
        if not check_sudo(message, SUDO_OWNER, bot):
            return
        FLAG_KEY = "otorgamiento_inicial_realizado"
        TOKENS = 200
        FICHAS = 50
        if get_config(FLAG_KEY) == "1":
            safe_reply(bot, message, obtener_texto("otorgar.ya_realizado"))
            return
        conn = get_connection()
        conn.execute("INSERT OR IGNORE INTO itsunario (user_id, tokens, fichas) SELECT user_id, 0, 0 FROM jugadores")
        conn.execute("UPDATE itsunario SET tokens = tokens + ?, fichas = fichas + ?", (TOKENS, FICHAS))
        afectados = conn.total_changes
        conn.commit()
        conn.close()
        set_config(FLAG_KEY, "1")
        msg = ItsukiLedger.render(
            "otorgar.exito_titulo",
            ["otorgar.exito_cuerpo"],
            variables={
                obtener_texto("otorgar.usuarios"): str(afectados),
                obtener_texto("otorgar.tokens"): str(TOKENS),
                obtener_texto("otorgar.fichas"): str(FICHAS),
            },
            user_id=message.from_user.id
        )
        safe_reply(bot, message, msg, parse_mode='HTML')

    @bot.message_handler(commands=['canal_marketing'])
    def canal_marketing(message):
        if not check_sudo(message, SUDO_COOWNER, bot):
            return
        parts = message.text.split(maxsplit=1)
        if len(parts) == 1:
            actual = get_config('canal_marketing') or obtener_texto("admin.no_configurado")
            return safe_reply(bot, message, obtener_texto("admin.canal_actual").replace('{canal}', actual))
        set_config('canal_marketing', parts[1])
        safe_reply(bot, message, obtener_texto("admin.canal_ok"))

    @bot.message_handler(commands=['canal_logs'])
    def canal_logs(message):
        if not check_sudo(message, SUDO_COOWNER, bot):
            return
        parts = message.text.split(maxsplit=1)
        if len(parts) == 1:
            actual = get_config('canal_logs') or obtener_texto("admin.no_configurado")
            return safe_reply(bot, message, obtener_texto("admin.canal_actual").replace('{canal}', actual))
        set_config('canal_logs', parts[1])
        safe_reply(bot, message, obtener_texto("admin.canal_ok"))

    @bot.message_handler(commands=['canal_admin'])
    def canal_admin(message):
        if not check_sudo(message, SUDO_COOWNER, bot):
            return
        parts = message.text.split(maxsplit=1)
        if len(parts) == 1:
            actual = get_config('canal_admin') or obtener_texto("admin.no_configurado")
            return safe_reply(bot, message, obtener_texto("admin.canal_actual").replace('{canal}', actual))
        set_config('canal_admin', parts[1])
        safe_reply(bot, message, obtener_texto("admin.canal_ok"))

    @bot.message_handler(commands=['groups'])
    def groups_cmd(message):
        if not check_sudo(message, SUDO_ADMIN, bot):
            return
        active = contar_grupos_activos()
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton('🔍 Ver activos', callback_data='panel_groups_list'))
        markup.add(types.InlineKeyboardButton('⏸ Desactivar último', callback_data='panel_groups_deactivate_last'))
        markup.add(types.InlineKeyboardButton('🔑 Generar Key', callback_data='panel_genkey'))
        safe_reply(bot, message, obtener_texto("admin.groups_activos").replace('{activos}', str(active)), reply_markup=markup)

    @bot.message_handler(commands=['kick_sector'])
    def kick_sector(message):
        if not check_sudo(message, SUDO_ADMIN, bot):
            return
        parts = message.text.split()
        if len(parts) < 2:
            return safe_reply(bot, message, obtener_texto("admin.kick_uso"))
        target = parts[1]
        desactivar_grupo(target)
        try:
            bot.leave_chat(target)
            safe_reply(bot, message, obtener_texto("admin.kick_ok").replace('{chat_id}', target))
        except Exception as e:
            safe_reply(bot, message, obtener_texto("admin.kick_error").replace('{error}', str(e)))

    @bot.message_handler(commands=['ban_user'])
    def ban_user(message):
        if not check_sudo(message, SUDO_COOWNER, bot):
            return
        parts = message.text.split()
        if len(parts) != 2:
            return safe_reply(bot, message, obtener_texto("admin.ban_uso"))
        try:
            uid = int(parts[1])
        except ValueError:
            return safe_reply(bot, message, "ID inválido.")
        set_sudo_level(uid, 0)
        safe_reply(bot, message, obtener_texto("admin.ban_ok").replace('{uid}', str(uid)))

    @bot.message_handler(commands=['verificar_grupos'])
    def verificar_grupos(message):
        if not check_sudo(message, SUDO_ADMIN, bot):
            return
        todos = obtener_todos_chat_ids()
        activos = []
        for cid in todos:
            try:
                bot.get_chat(cid)
                activos.append(cid)
            except:
                eliminar_grupo_por_id(cid)
        safe_reply(bot, message, obtener_texto("admin.verificar_ok").replace('{activos}', str(len(activos))))

    @bot.message_handler(commands=['cleanup_salas'])
    def cleanup_salas(message):
        if not check_sudo(message, SUDO_ADMIN, bot):
            return
        if salas is None or salas_lock is None:
            return safe_reply(bot, message, "Función no disponible en esta configuración.")
        with salas_lock:
            eliminadas = 0
            for cid in list(salas.keys()):
                try:
                    bot.get_chat(cid)
                except:
                    for uid in salas[cid].get('jugadores', {}):
                        safe_reply(bot, uid, obtener_texto("i18n_kernel_sala_eliminada"))
                    del salas[cid]
                    # eliminar_sala(cid) asume que existe en core.db
                    from core.db import eliminar_sala
                    eliminar_sala(cid)
                    eliminadas += 1
        safe_reply(bot, message, obtener_texto("admin.cleanup_ok").replace('{n}', str(eliminadas)))

    @bot.message_handler(commands=['analityc'])
    def analityc_cmd(message):
        if not check_sudo(message, SUDO_ADMIN, bot):
            return
        try:
            import psutil
            ram = psutil.virtual_memory()
            cpu = psutil.cpu_percent(interval=0.1)
            disk = psutil.disk_usage('/')
            uptime = time.time() - psutil.boot_time()
        except ImportError:
            ram = None
            cpu = None
            disk = None
            uptime = None
        grupos = contar_grupos_activos()
        if ram:
            msg = (
                f"📊 **REPORTE DE SALUD**\n"
                f"🧠 RAM: {ram.used // (1024 * 1024)} MB / {ram.total // (1024 * 1024)} MB ({ram.percent}%)\n"
                f"⚙️ CPU: {cpu}%\n"
                f"💾 Disco: {disk.free // (1024 * 1024)} MB libres ({disk.percent}% usado)\n"
                f"🏛️ Grupos activos: {grupos}\n"
                f"⏱️ Uptime: {int(uptime // 3600)}h {int(uptime % 3600 // 60)}m"
            )
        else:
            msg = f"📊 Grupos activos: {grupos}\n(psutil no instalado para más métricas)"
        safe_reply(bot, message, msg, parse_mode='HTML')

    # Callbacks del panel de grupos
    @bot.callback_query_handler(func=lambda call: call.data.startswith('panel_'))
    def panel_callback(call):
        uid = call.from_user.id
        if get_sudo_level(uid) < SUDO_ADMIN:
            return bot.answer_callback_query(call.id, obtener_texto(MENSAJE_PERMISO, user_id=uid))
        data = call.data
        if data == 'panel_genkey':
            if get_sudo_level(uid) < SUDO_OWNER:
                return bot.answer_callback_query(call.id, obtener_texto("admin.genkey_solo_owner"))
            key = generar_key("standard")
            bot.answer_callback_query(call.id, f"Key: {key}", show_alert=True)
            safe_reply(bot, call.message, obtener_texto("admin.genkey_ok").replace('{key}', key), parse_mode='HTML')
            return
        if data == 'panel_groups_list':
            return _mostrar_pagina_grupos(call, 0)
        if data.startswith('panel_groups_list_'):
            page = int(data.split('_')[-1])
            return _mostrar_pagina_grupos(call, page)
        if data == 'panel_groups_deactivate_last':
            ultimo = obtener_ultimo_grupo_activo()
            if ultimo:
                desactivar_grupo(ultimo)
                bot.answer_callback_query(call.id, f"Grupo {ultimo} desactivado.")
                # Refrescar vista
                return _mostrar_pagina_grupos(call, 0)
            else:
                bot.answer_callback_query(call.id, obtener_texto("admin.no_grupos_activos"))
                return
        if data == 'panel_refresh_names':
            ids = obtener_ids_sin_nombre()
            actualizados = 0
            for cid in ids:
                try:
                    chat = bot.get_chat(cid)
                    actualizar_nombre_grupo(cid, chat.title or str(cid))
                    actualizados += 1
                except:
                    pass
            bot.answer_callback_query(call.id, f'{actualizados} nombres actualizados.')
            return _mostrar_pagina_grupos(call, 0)
        if data == 'panel_groups_back':
            active = contar_grupos_activos()
            markup = types.InlineKeyboardMarkup()
            markup.add(types.InlineKeyboardButton('🔍 Ver activos', callback_data='panel_groups_list'))
            markup.add(types.InlineKeyboardButton('⏸ Desactivar último', callback_data='panel_groups_deactivate_last'))
            markup.add(types.InlineKeyboardButton('🔑 Generar Key', callback_data='panel_genkey'))
            bot.edit_message_text(
                obtener_texto("admin.groups_activos").replace('{activos}', str(active)),
                call.message.chat.id, call.message.message_id, reply_markup=markup
            )
            return

    def _mostrar_pagina_grupos(call, page=0, limite=5):
        total = contar_todos_grupos()
        grupos = obtener_grupos_paginados(limite, page * limite)
        if not grupos:
            bot.edit_message_text(obtener_texto("admin.no_grupos"), call.message.chat.id, call.message.message_id)
            return
        texto = '🏛️ **NÚCLEOS DETECTADOS:**\n'
        for cid, nombre, estado in grupos:
            if not nombre:
                try:
                    chat = bot.get_chat(cid)
                    nombre = chat.title or str(cid)
                    actualizar_nombre_grupo(cid, nombre)
                except:
                    nombre = f'ID: {cid}'
            icono = '🟢' if estado == 'ACTIVO' else '⚪'
            texto += f'{icono} `{nombre}`\n'
        texto += f'\nPág. {page + 1} de {max(1, (total + limite - 1) // limite)}'
        markup = types.InlineKeyboardMarkup(row_width=3)
        botones = []
        if page > 0:
            botones.append(types.InlineKeyboardButton('<< Ant.', callback_data=f'panel_groups_list_{page - 1}'))
        if (page + 1) * limite < total:
            botones.append(types.InlineKeyboardButton('Sig. >>', callback_data=f'panel_groups_list_{page + 1}'))
        botones.append(types.InlineKeyboardButton('🔄 Refrescar', callback_data='panel_refresh_names'))
        botones.append(types.InlineKeyboardButton('🔙 Volver', callback_data='panel_groups_back'))
        botones.append(types.InlineKeyboardButton('🔑 Key', callback_data='panel_genkey'))
        markup.add(*botones)
        bot.edit_message_text(texto, call.message.chat.id, call.message.message_id, reply_markup=markup, parse_mode='Markdown')

logger.info("Módulo admin cargado.")