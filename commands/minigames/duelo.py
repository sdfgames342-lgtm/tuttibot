import random, time, logging
from core.db import (
    get_connection, duelo_activo, obtener_respuesta_duelo, finalizar_duelo,
    actualizar_puntos_jugador, penalizar_puntos, sumar_puntos_grupo
)
from utils.idiomas import obtener_texto, obtener_idioma_chat
from .data import IDIOMS

logger = logging.getLogger(__name__)

def iniciar_duelo(chat_id, bot, msg_queue):
    if duelo_activo(chat_id):
        return
    lang = obtener_idioma_chat(chat_id)
    if lang == 'es':
        pares = [k for k in IDIOMS if k.startswith('en->es') or k.startswith('es->en')]
    else:
        pares = [k for k in IDIOMS if k.startswith('en->pt') or k.startswith('pt->en')]
    if not pares:
        return
    par = random.choice(pares)
    frase_obj = random.choice(IDIOMS[par])
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        'INSERT OR REPLACE INTO duelo_traduccion_salas (chat_id, activa, frase, respuesta, inicio_epoch) VALUES (?,1,?,?,?)',
        (chat_id, frase_obj['frase'], frase_obj['resp'], time.time()))
    conn.commit()
    conn.close()
    msg_text = obtener_texto('hardcoded.minigames_duelo_title').replace('{frase}', frase_obj['frase'])
    msg_queue.put(bot.send_message, chat_id, msg_text + '\n\n' + obtener_texto('hardcoded.minigames_duelo_tiempo'), parse_mode='Markdown')

def evaluar_duelo(chat_id, user_id, texto, bot, msg_queue):
    resp = obtener_respuesta_duelo(chat_id)
    if not resp:
        return
    if texto.strip().lower() != resp.lower():
        penalizar_puntos(user_id, 0.95)
        msg_queue.put(bot.send_message, chat_id, obtener_texto('hardcoded.minigames_44'))
        return
    puntos = 60
    actualizar_puntos_jugador(user_id, puntos)
    sector_pts = int(puntos * 1.5)
    sumar_puntos_grupo(chat_id, sector_pts)
    finalizar_duelo(chat_id)
    msg_win = obtener_texto('hardcoded.minigames_duelo_win').replace('{user_id}', str(user_id)).replace('{puntos}', str(puntos)).replace('{sector_pts}', str(sector_pts))
    msg_queue.put(bot.send_message, chat_id, msg_win)
