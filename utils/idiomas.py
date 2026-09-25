import json, os, sqlite3, threading
from dotenv import load_dotenv
load_dotenv()
DB_PATH = os.getenv('DATABASE_PATH', 'tutti_game.db')
IDIOMAS = {'es': 'es.json', 'pt': 'pt.json'}
IDIOMA_POR_DEFECTO = 'es'
_cache = {}
_cache_lock = threading.Lock()
_preferencias_cache = {}
_prefs_lock = threading.Lock()

def cargar_textos(lang: str):
    if lang not in _cache:
        archivo = IDIOMAS.get(lang, IDIOMAS[IDIOMA_POR_DEFECTO])
        ruta = os.path.join(os.path.dirname(__file__), '..', 'idiomas', archivo)
        with open(ruta, 'r', encoding='utf-8') as f:
            data = json.load(f)
        with _cache_lock:
            _cache[lang] = data
    return _cache[lang]

def obtener_texto(clave: str, lang: str=None, chat_id: str=None, user_id: int=None):
    if lang is None:
        if chat_id:
            lang = obtener_idioma_chat(chat_id)
        elif user_id:
            lang = obtener_idioma_usuario(user_id)
        else:
            lang = IDIOMA_POR_DEFECTO
    textos = cargar_textos(lang)
    keys = clave.split('.')
    valor = textos
    for key in keys:
        if isinstance(valor, dict) and key in valor:
            valor = valor[key]
        else:
            return f'[{clave}]'
    return valor if isinstance(valor, str) else f'[{clave}]'

def formatear_texto(clave: str, lang: str=None, chat_id: str=None, user_id: int=None, **kwargs):
    texto = obtener_texto(clave, lang=lang, chat_id=chat_id, user_id=user_id)
    try:
        return texto.format(**kwargs)
    except (KeyError, ValueError):
        return texto

def obtener_idioma_chat(chat_id: str) -> str:
    chat_id = str(chat_id)
    if chat_id in _preferencias_cache:
        return _preferencias_cache[chat_id]
    from core.db import get_config
    lang = get_config(f'lang_chat_{chat_id}') or IDIOMA_POR_DEFECTO
    with _prefs_lock:
        _preferencias_cache[chat_id] = lang
    return lang

def obtener_idioma_usuario(user_id: int) -> str:
    key = f'user_{user_id}'
    if key in _preferencias_cache:
        return _preferencias_cache[key]
    from core.db import get_config
    lang = get_config(f'lang_user_{user_id}') or IDIOMA_POR_DEFECTO
    with _prefs_lock:
        _preferencias_cache[key] = lang
    return lang

def establecer_idioma_chat(chat_id: str, lang: str):
    from core.db import set_config
    set_config(f'lang_chat_{chat_id}', lang)
    with _prefs_lock:
        _preferencias_cache[str(chat_id)] = lang

def establecer_idioma_usuario(user_id: int, lang: str):
    from core.db import set_config
    set_config(f'lang_user_{user_id}', lang)
    with _prefs_lock:
        _preferencias_cache[f'user_{user_id}'] = lang
