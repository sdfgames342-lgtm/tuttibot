import os, re, logging, tempfile, time
from telebot import types
from yt_dlp import YoutubeDL
from utils.idiomas import obtener_texto
from utils.reply_helper import safe_reply
from utils.formatters import to_mono_font
from core.db import (
    usuario_puede_descargar, usuario_descarga_hoy, registrar_descarga,
    obtener_saldo_itsunario, sumar_itsunario, get_config, get_connection
)

logger = logging.getLogger(__name__)
MAX_DURATION = 600
TEMP_DIR = tempfile.gettempdir()

HELP_COMMANDS = [
    {"command": "/ytmusic", "desc_key": "help.desc_ytmusic", "sudo_level": 0, "category": "otros"}
]

def puede_descargar(user_id):
    if usuario_puede_descargar(user_id):
        return (True, None)
    conn = get_connection()
    cur = conn.execute("SELECT valor FROM itsunario_limites WHERE clave='ytmusic_gratis_diario'")
    row = cur.fetchone()
    limite = int(row[0]) if row else 5
    conn.close()
    descargas_hoy = usuario_descarga_hoy(user_id)
    if descargas_hoy < limite:
        return (True, None)
    tokens, fichas = obtener_saldo_itsunario(user_id)
    inflacion = float(get_config('inflacion_actual') or 0)
    precio1 = max(1, int(5 * (1 + inflacion / 100)))
    precio5 = max(3, int(20 * (1 + inflacion / 100)))
    precio20 = max(10, int(60 * (1 + inflacion / 100)))
    msg = obtener_texto('ytmusic.limite_diario', tokens=tokens, fichas=fichas,
                        limite=limite, precio1=precio1, precio5=precio5, precio20=precio20)
    return (False, msg)

def descargar_audio(url, callback_progreso=None):
    with YoutubeDL({'quiet': True}) as ydl:
        info = ydl.extract_info(url, download=False)
        if info.get('duration', 0) > MAX_DURATION:
            raise ValueError(obtener_texto('ytmusic.duracion_excedida'))
    output_template = os.path.join(TEMP_DIR, 'itsuki_audio_%(id)s.%(ext)s')
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': output_template,
        'postprocessors': [{'key': 'FFmpegExtractAudio', 'preferredcodec': 'opus', 'preferredquality': '64'}],
        'quiet': True,
        'no_warnings': True,
        'progress_hooks': [callback_progreso] if callback_progreso else []
    }
    with YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        filepath = ydl.prepare_filename(info).replace('.webm', '.opus').replace('.m4a', '.opus').replace('.mp3', '.opus')
        if not os.path.exists(filepath):
            filepath = os.path.splitext(filepath)[0] + '.opus'
        return filepath, info

def progress_hook(d, message_id, chat_id, bot):
    if d['status'] == 'downloading':
        try:
            bot.edit_message_text(obtener_texto('hardcoded.ytmusic_descargando').replace('{percent}', d['_percent_str']),
                                  chat_id, message_id)
        except: pass
    elif d['status'] == 'finished':
        try:
            bot.edit_message_text(obtener_texto('hardcoded.ytmusic_convirtiendo'), chat_id, message_id)
        except: pass

def buscar_videos(query, limit=5):
    with YoutubeDL({'quiet': True, 'extract_flat': False, 'skip_download': True}) as ydl:
        info = ydl.extract_info(f'ytsearch{limit}:{query}', download=False)
        results = []
        for entry in info.get('entries', []):
            results.append({
                'id': entry.get('id'),
                'title': entry.get('title'),
                'uploader': entry.get('uploader'),
                'duration': entry.get('duration', 0),
                'url': entry.get('webpage_url')
            })
        return results

def consumir_credito(user_id):
    conn = get_connection()
    cur = conn.execute("SELECT id FROM itsunario_canjes WHERE user_id=? AND tipo='ytmusic_credito' LIMIT 1", (user_id,))
    row = cur.fetchone()
    if row:
        conn.execute("DELETE FROM itsunario_canjes WHERE id=?", (row[0],))
        conn.commit()
        conn.close()
        return True
    conn.close()
    return False

def iniciar_descarga(bot, message, url):
    user_id = message.from_user.id
    chat_id = message.chat.id
    if consumir_credito(user_id):
        ok, msg = True, None
    else:
        ok, msg = puede_descargar(user_id)
    if not ok:
        return safe_reply(bot, message, msg)
    status_msg = safe_reply(bot, message, obtener_texto('hardcoded.ytmusic_analizando'))
    mid = status_msg.message_id
    def hook(d): progress_hook(d, mid, chat_id, bot)
    temp_file = None
    try:
        filepath, info = descargar_audio(url, callback_progreso=hook)
        temp_file = filepath
        caption = f'🎤 {to_mono_font(info.get("title", "Audio"))}\n👤 {to_mono_font(info.get("uploader", ""))}\n🔗 {message.from_user.first_name}'
        with open(filepath, 'rb') as audio:
            bot.send_voice(chat_id, audio, caption=caption, duration=info.get('duration', 0), timeout=30)
        registrar_descarga(user_id)
        bot.delete_message(chat_id, mid)
    except Exception as e:
        logger.exception('Error en ytmusic')
        safe_reply(bot, message, obtener_texto('hardcoded.ytmusic_error_procesar').replace('{error}', str(e)))
    finally:
        if temp_file and os.path.exists(temp_file):
            try: os.remove(temp_file)
            except: pass

def cmd_comprar_paquete(message):
    uid = message.from_user.id
    parts = message.text.split()
    if len(parts) < 3:
        return safe_reply(bot, message, obtener_texto('ytmusic.comprar_uso'))
    try:
        cantidad = int(parts[2])
    except ValueError:
        return safe_reply(bot, message, obtener_texto('ytmusic.cantidad_invalida'))
    inflacion = float(get_config('inflacion_actual') or 0)
    precios = {
        1: max(1, int(5 * (1 + inflacion / 100))),
        5: max(3, int(20 * (1 + inflacion / 100))),
        20: max(10, int(60 * (1 + inflacion / 100)))
    }
    if cantidad not in precios:
        return safe_reply(bot, message, obtener_texto('ytmusic.paquete_invalido'))
    precio = precios[cantidad]
    tokens, fichas = obtener_saldo_itsunario(uid)
    if tokens < precio:
        return safe_reply(bot, message, obtener_texto('ytmusic.tokens_insuficientes', tokens=tokens, precio=precio))
    sumar_itsunario(uid, tokens=-precio)
    conn = get_connection()
    for _ in range(cantidad):
        conn.execute("INSERT INTO itsunario_canjes (user_id, tipo, cantidad_tokens) VALUES (?, 'ytmusic_credito', 0)", (uid,))
    conn.commit()
    conn.close()
    safe_reply(bot, message, obtener_texto('ytmusic.compra_exito', cantidad=cantidad, precio=precio))

def register_handlers(bot, register_command=None, msg_queue=None):
    if register_command is None:
        def register_command(name): return bot.message_handler(commands=[name])
    if msg_queue is None:
        class DummyQueue:
            def put(self, fn, *args, **kwargs): return fn(*args, **kwargs)
        msg_queue = DummyQueue()

    @register_command('ytmusic')
    def ytmusic_cmd(message):
        texto = message.text.strip()
        match = re.search(r'(https?://)?(www\.)?(youtube\.com/watch\?v=|youtu\.be/)[\w-]+', texto)
        if match:
            url = match.group(0)
            if not url.startswith('http'): url = 'https://' + url
            iniciar_descarga(bot, message, url)
            return
        if len(texto.split()) >= 2 and texto.split()[1].lower() == 'comprar':
            return cmd_comprar_paquete(message)
        parts = texto.split(maxsplit=1)
        query = parts[1] if len(parts) > 1 else ''
        if not query.strip():
            return safe_reply(bot, message, obtener_texto('hardcoded.ytmusic_uso'), parse_mode='HTML')
        try:
            results = buscar_videos(query)
        except Exception as e:
            logger.exception('Error buscando videos')
            return safe_reply(bot, message, obtener_texto('hardcoded.ytmusic_error_busqueda'))
        if not results:
            return safe_reply(bot, message, obtener_texto('hardcoded.ytmusic_sin_resultados'))
        markup = types.InlineKeyboardMarkup(row_width=1)
        for i, video in enumerate(results):
            lbl = f"{video['title']} ({video['uploader']})"
            if len(lbl) > 64: lbl = lbl[:61] + '...'
            markup.add(types.InlineKeyboardButton(lbl, callback_data=f'ytpick_{i}'))
        markup.add(types.InlineKeyboardButton('⌫ Cancelar', callback_data='ytpick_cancel'))
        if not hasattr(bot, '_yt_cache'): bot._yt_cache = {}
        bot._yt_cache[message.chat.id] = results
        safe_reply(bot, message, obtener_texto('hardcoded.ytmusic_resultados'), reply_markup=markup)

    @bot.callback_query_handler(func=lambda call: call.data.startswith('ytpick_'))
    def yt_search_callback(call):
        chat_id = call.message.chat.id
        data = call.data
        if data == 'ytpick_cancel':
            bot.edit_message_text(obtener_texto('hardcoded.ytmusic_cancelada'), chat_id, call.message.message_id)
            return
        idx = int(data.split('_')[1])
        results = bot._yt_cache.get(chat_id)
        if not results or idx >= len(results):
            bot.answer_callback_query(call.id, obtener_texto("i18n_ytmusic_opcion_invalida"))
            return
        video = results[idx]
        url = video['url']
        try: bot.edit_message_text(f"🎶 Cargando: {video['title']}", chat_id, call.message.message_id)
        except: pass
        class FakeMessage:
            def __init__(self, chat_id, from_user):
                self.chat = types.Chat(id=chat_id, type='private')
                self.from_user = from_user
        fake_msg = FakeMessage(chat_id, call.from_user)
        iniciar_descarga(bot, fake_msg, url)
