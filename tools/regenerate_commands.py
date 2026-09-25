#!/usr/bin/env python3
"""
Regenera todos los comandos extraídos desde cero usando el código
original mostrado en la conversación. Corrige indentación y actualiza main.py.
"""
import re
from pathlib import Path

BASE = Path(".")
COMMANDS_DIR = BASE / "commands"
MAIN_PY = BASE / "main.py"

# ─── 1. Contenido exacto de los comandos (extraído del historial) ───
# Se ha limpiado la indentación para que sea consistente (4 espacios por nivel)

COMMAND_SOURCES = {
    "testsizania": '''
from telebot import types
from utils.reply_helper import safe_reply
from utils.db_handler import get_sudo_level
from utils.sizania import ejecutar_sizaña, FRASES_GLOBALES
import logging, psutil, time, random

logger = logging.getLogger(__name__)

def register_testsizania_handlers(bot, register_command=None):
    @bot.message_handler(commands=['testsizania'])
    def testsizania_cmd(message):
        if get_sudo_level(message.from_user.id) < 2:
            return bot.reply_to(message, "⛔ Acceso denegado (Admin+).")
        import psutil, time
        uptime = time.time() - psutil.Process().create_time()
        horas = int(uptime // 3600)
        minutos = int((uptime % 3600) // 60)
        frase = random.choice(FRASES_GLOBALES)
        texto = f"// [ 📢 COMUNICADO ITS ] //\\n⏱️ Uptime: {horas}h {minutos}m\\n\\n{frase}"
        from utils.control_grupos import get_connection
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT chat_id FROM control_grupos WHERE estado='ACTIVO'")
        activos = [row[0] for row in cur.fetchall()]
        conn.close()
        if not activos:
            return bot.reply_to(message, "No hay grupos activos.")
        for chat_id in activos:
            try:
                if message.photo:
                    msg_queue.put(bot.send_photo, chat_id, message.photo[-1].file_id, caption=texto)
                else:
                    msg_queue.put(bot.send_message, chat_id, texto)
            except Exception as e:
                logger.warning(f"No se pudo enviar a {chat_id}: {e}")
        bot.reply_to(message, f"✅ Sizaña enviada a {len(activos)} grupos.")
''',

    "setimg": '''
from telebot import types
from utils.reply_helper import safe_reply
from utils.db_handler import get_sudo_level
from utils.imagenes import guardar_imagen
import logging

logger = logging.getLogger(__name__)

def register_setimg_handlers(bot, register_command=None):
    @bot.message_handler(commands=['setimg'])
    def setimg_cmd(message):
        if get_sudo_level(message.from_user.id) < 3:
            return safe_reply(bot, message, '⛔ Solo Co-Owner o superior pueden configurar imágenes.')
        parts = message.text.split()
        if len(parts) < 2:
            return safe_reply(bot, message, 'Uso: /setimg <comando> (responde a una imagen o adjuntala)')
        comando = parts[1].lower()
        if comando not in ['start', 'about', 'help', 'premium']:
            return safe_reply(bot, message, 'Comandos válidos: start, about, help, premium')
        if message.reply_to_message and message.reply_to_message.photo:
            file_id = message.reply_to_message.photo[-1].file_id
        elif message.photo:
            file_id = message.photo[-1].file_id
        else:
            return safe_reply(bot, message, 'Debes adjuntar o responder a una imagen.')
        guardar_imagen(comando, file_id)
        safe_reply(bot, message, f'✅ Imagen para /{comando} actualizada.')
''',

    "afinidad": '''
from telebot import types
from utils.reply_helper import safe_reply
from utils.db_handler import obtener_afinidad
import logging

logger = logging.getLogger(__name__)

def register_afinidad_handlers(bot, register_command=None):
    @bot.message_handler(commands=['afinidad'])
    def afinidad_cmd(message):
        user_id = message.reply_to_message.from_user.id if message.reply_to_message else message.from_user.id
        nivel = obtener_afinidad(user_id)
        if nivel >= 80:
            emoji = '🌸'; comentario = 'Eres... tolerable. Incluso agradable de procesar.'
        elif nivel >= 50:
            emoji = '📊'; comentario = 'Tus datos empiezan a ser interesantes.'
        elif nivel >= 20:
            emoji = '🔍'; comentario = 'Estás bajo observación. No me decepciones.'
        else:
            emoji = '💤'; comentario = 'Eres ruido de fondo. Apenas te registro.'
        safe_reply(bot, message, f'{emoji} Afinidad con Itsuki: {nivel}/100\\n\\n{comentario}')
''',

    "sponsor": '''
from telebot import types
from utils.reply_helper import safe_reply
from utils.db_handler import get_config, generar_key, get_sudo_level
from utils.formatters import ItsukiBot
import logging

logger = logging.getLogger(__name__)

def register_sponsor_handlers(bot, register_command=None):
    @bot.message_handler(commands=['sponsor'])
    def sponsor_cmd(message):
        if message.chat.type != 'private':
            return safe_reply(bot, message, "Este comando solo funciona en privado.")
        user = message.from_user
        admin_channel = get_config("canal_admin")
        if not admin_channel:
            return safe_reply(bot, message, "El canal de administración no está configurado.")
        markup = types.InlineKeyboardMarkup()
        markup.add(
            types.InlineKeyboardButton("✅ Aprobar", callback_data=f"sponsor_approve_{user.id}"),
            types.InlineKeyboardButton("❌ Rechazar", callback_data=f"sponsor_reject_{user.id}")
        )
        texto = (
            f"📩 **Solicitud de Patrocinio**\\n"
            f"Usuario: {user.first_name} (ID: `{user.id}`)\\n"
            f"Username: @{user.username or 'sin'}\\n\\n"
            "¿Autorizar la entrega de una key de activación?"
        )
        msg_queue.put(bot.send_message, admin_channel, texto, parse_mode="Markdown", reply_markup=markup)
        safe_reply(bot, message, "Tu solicitud ha sido enviada al operador. Aguardá la respuesta.")
''',

    "genkey": '''
from telebot import types
from utils.reply_helper import safe_reply
from utils.db_handler import get_sudo_level, generar_key
import logging

logger = logging.getLogger(__name__)

def register_genkey_handlers(bot, register_command=None):
    @bot.message_handler(commands=['genkey'])
    def genkey_cmd(message):
        if get_sudo_level(message.from_user.id) < 4:
            return safe_reply(bot, message, "⛔ Solo el Owner puede generar keys.")
        key = generar_key(message.from_user.id)
        safe_reply(bot, message, f"🔑 Nueva key (24h):\\n`{key}`", parse_mode="Markdown")
''',

    "activar": '''
from telebot import types
from utils.reply_helper import safe_reply
from utils.control_grupos import validar_key, registrar_grupo, activar_grupo
from utils.idiomas import obtener_texto
import logging

logger = logging.getLogger(__name__)

def register_activar_handlers(bot, register_command=None):
    @bot.message_handler(commands=['activar'])
    def activar_cmd(message):
        if message.chat.type == 'private':
            return
        parts = message.text.split()
        if len(parts) != 2:
            return safe_reply(bot, message, "Uso: /activar <key>")
        key = parts[1].strip()
        chat_id = str(message.chat.id)
        if validar_key(key, marcar_usada=False):
            nombre = getattr(message.chat, 'title', None)
            pending_activations[chat_id] = {'nombre': nombre, 'activado': False, 'key': key}
            markup = types.InlineKeyboardMarkup()
            markup.add(
                types.InlineKeyboardButton(obtener_texto("legal.accept_btn"), callback_data=f"legal_accept_{chat_id}")
            )
            safe_reply(bot, message, obtener_texto("legal.key_activation"), reply_markup=markup, parse_mode='HTML')
        else:
            safe_reply(bot, message, "❌ Key inválida o expirada.")
''',

    "unir": '''
from telebot import types
from utils.reply_helper import safe_reply
from utils.db_handler import registrar_jugador, jugador_en_otra_sala
from utils.idiomas import obtener_texto, formatear_texto
import logging

logger = logging.getLogger(__name__)

def register_unir_handlers(bot, register_command=None):
    @bot.message_handler(commands=['unir'])
    def unir_jugador(message):
        chat_id = str(message.chat.id)
        user_id = message.from_user.id
        if chat_id not in salas or salas[chat_id]['estado'] != 'ESPERA':
            return
        sala = salas[chat_id]
        if len(sala['jugadores']) >= 9:
            safe_reply(bot, message, obtener_texto('join.max_players'))
            return
        if jugador_en_otra_sala(user_id, chat_id):
            safe_reply(bot, message, obtener_texto('join.already_in_other_room'))
            return
        nombre = message.from_user.first_name or message.from_user.username or f"Aspirante_{user_id}"
        sala['jugadores'][user_id] = nombre
        registrar_jugador(user_id, nombre)
        safe_reply(bot, message, formatear_texto('join.joined', player=nombre, count=len(sala['jugadores'])))
''',

    "cagon": '''
from telebot import types
from utils.reply_helper import safe_reply
from utils.db_handler import eliminar_sala
import logging

logger = logging.getLogger(__name__)

def register_cagon_handlers(bot, register_command=None):
    @bot.message_handler(commands=['cagon'])
    def cagon_cmd(message):
        chat_id = str(message.chat.id)
        user_id = message.from_user.id
        sala = salas.get(chat_id)
        if not sala or sala['estado'] != 'ESPERA':
            return safe_reply(bot, message, "No se puede abandonar en este momento.")
        if user_id not in sala['jugadores']:
            return safe_reply(bot, message, "No estás en la sala.")
        if user_id == sala['creador']:
            del salas[chat_id]
            eliminar_sala(chat_id)
            safe_reply(bot, message, "El creador abandonó la sala. Sala eliminada.")
        else:
            nombre = sala['jugadores'].pop(user_id)
            safe_reply(bot, message, f"{nombre} abandonó la sala ({len(sala['jugadores'])} jugadores).")
''',

    "off": '''
from telebot import types
from utils.reply_helper import safe_reply
from utils.db_handler import eliminar_sala
import logging

logger = logging.getLogger(__name__)

def register_off_handlers(bot, register_command=None):
    @bot.message_handler(commands=['off'])
    def off_cmd(message):
        chat_id = str(message.chat.id)
        user_id = message.from_user.id
        sala = salas.get(chat_id)
        if not sala:
            return safe_reply(bot, message, "No hay partida activa.")
        if user_id != sala['creador']:
            if message.chat.type != 'private':
                try:
                    miembro = bot.get_chat_member(chat_id, user_id)
                    if miembro.status not in ['administrator', 'creator']:
                        return safe_reply(bot, message, "Sin permisos.")
                except:
                    return safe_reply(bot, message, "Error al verificar permisos.")
            else:
                return safe_reply(bot, message, "Solo el creador puede cancelar en privado.")
        for uid in sala['jugadores']:
            try:
                safe_reply(bot, uid, "⚠️ La partida ha sido cancelada.")
            except:
                pass
        del salas[chat_id]
        eliminar_sala(chat_id)
        safe_reply(bot, message, "Partida cancelada.")
'''
}

# ─── 2. Escribir cada archivo en commands/ ───
for cmd, source in COMMAND_SOURCES.items():
    # Limpiar indentación inicial (las cadenas triples tienen espacios al principio)
    lines = source.strip().splitlines()
    # Eliminar primera línea si está vacía
    if lines and lines[0] == '':
        lines = lines[1:]
    # Determinar indentación mínima (ignorar líneas vacías)
    min_indent = min((len(line) - len(line.lstrip())) for line in lines if line.strip()) if lines else 0
    # Quitar esa indentación a todas las líneas
    cleaned = []
    for line in lines:
        if line.strip() == '':
            cleaned.append('')
        else:
            cleaned.append(line[min_indent:])
    content = '\n'.join(cleaned) + '\n'
    file_path = COMMANDS_DIR / f"{cmd}.py"
    file_path.write_text(content)
    print(f"✅ {cmd}.py regenerado")

# ─── 3. Mover comandos de core/cards.py ───
cards_file = BASE / "core" / "cards.py"
if cards_file.exists():
    cards_content = cards_file.read_text()
    # Buscar cada handler en cards.py
    for cmd in ['registrarcarta', 'listarcartas', 'borrarcarta']:
        # Regex mejorada para capturar el bloque completo (decorador + función)
        pattern = rf"(@bot\.message_handler\(commands=\['{cmd}'\]\)\s*\n\s*def {cmd}_cmd\(message\):.*?\n(?:    .*\n|\n)*?(?=\n@|\n\Z))"
        match = re.search(pattern, cards_content, re.DOTALL)
        if match:
            block = match.group(0)
            # Crear archivo en commands/
            dest = COMMANDS_DIR / f"{cmd}.py"
            if not dest.exists():
                # Preparar contenido con función registradora
                # Extraer cuerpo indentado
                lines = block.splitlines(keepends=True)
                # Encontrar def
                func_start = None
                for i, line in enumerate(lines):
                    if line.strip().startswith(f"def {cmd}_cmd(message):"):
                        func_start = i
                        break
                if func_start is not None:
                    body = ''.join(lines[func_start+1:])
                    # Construir nuevo archivo
                    new_content = f'''from telebot import types
from utils.reply_helper import safe_reply
import logging

logger = logging.getLogger(__name__)

def register_{cmd}_handlers(bot, register_command=None):
    @bot.message_handler(commands=['{cmd}'])
    def {cmd}_cmd(message):
{body}
'''
                    dest.write_text(new_content)
                    print(f"✅ {cmd}.py movido desde cards.py")
                    # Eliminar de cards.py
                    cards_content = cards_content.replace(block, "")
    cards_file.write_text(cards_content)

# ─── 4. Actualizar main.py ───
# Eliminar los handlers antiguos de main.py (si existieran)
main_content = MAIN_PY.read_text()
for cmd in COMMAND_SOURCES:
    # Eliminar cualquier bloque residual que coincida
    main_content = re.sub(rf"@bot\.message_handler\(commands=\['{cmd}'\]\).*?(?=\n@|\n#|\Z)", "", main_content, flags=re.DOTALL)

# Agregar imports
new_imports = []
for cmd in COMMAND_SOURCES:
    new_imports.append(f"from commands.{cmd} import register_{cmd}_handlers")
for cmd in ['registrarcarta', 'listarcartas', 'borrarcarta']:
    if (COMMANDS_DIR / f"{cmd}.py").exists():
        new_imports.append(f"from commands.{cmd} import register_{cmd}_handlers")

lines = main_content.splitlines(keepends=True)
insert_pos = 0
for i, line in enumerate(lines):
    if line.strip().startswith('from commands.') or line.strip().startswith('import '):
        insert_pos = i + 1
for imp in new_imports:
    if imp not in main_content:
        lines.insert(insert_pos, imp + '\n')
        insert_pos += 1
main_content = ''.join(lines)

# Agregar llamadas de registro
register_calls = []
for cmd in COMMAND_SOURCES:
    register_calls.append(f"register_{cmd}_handlers(bot, register_command)")
for cmd in ['registrarcarta', 'listarcartas', 'borrarcarta']:
    if (COMMANDS_DIR / f"{cmd}.py").exists():
        register_calls.append(f"register_{cmd}_handlers(bot, register_command)")

for reg in register_calls:
    if reg not in main_content:
        main_content = main_content.replace("if __name__", f"{reg}\nif __name__")

MAIN_PY.write_text(main_content)
print("✅ main.py actualizado\n")

# ─── 5. Compilación final de verificación ───
import py_compile, sys
errors = []
for py_file in BASE.glob("commands/*.py"):
    if py_file.name == '__init__.py':
        continue
    try:
        py_compile.compile(str(py_file), doraise=True)
        print(f"✔️  {py_file} OK")
    except py_compile.PyCompileError as e:
        print(f"❌ {py_file} : {e}")
        errors.append(str(py_file))
try:
    py_compile.compile(str(MAIN_PY), doraise=True)
    print(f"✔️  main.py OK")
except py_compile.PyCompileError as e:
    print(f"❌ main.py : {e}")
    errors.append("main.py")

if errors:
    print(f"\n⚠️  {len(errors)} archivos con errores.")
else:
    print("\n🎉 Todos los archivos compilan correctamente.")
