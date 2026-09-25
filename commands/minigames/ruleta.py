import random, time, logging
from core.db import (
    get_connection, ruleta_activa, obtener_respuesta_ruleta, finalizar_ruleta,
    actualizar_puntos_jugador, penalizar_puntos, sumar_puntos_grupo
)
from utils.idiomas import obtener_texto, obtener_idioma_chat
from .data import EXAMENES

logger = logging.getLogger(__name__)

def iniciar_ruleta(chat_id, bot, msg_queue):
    if ruleta_activa(chat_id):
        return
    lang = obtener_idioma_chat(chat_id)
    examenes = EXAMENES.get(lang, EXAMENES['es'])
    examen = random.choice(examenes)
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        'INSERT OR REPLACE INTO ruleta_rusa_salas (chat_id, activa, pregunta, respuesta, inicio_epoch) VALUES (?,1,?,?,?)',
        (chat_id, examen['pregunta'], examen['respuesta'], time.time()))
    conn.commit()
    conn.close()
    msg_text = obtener_texto('hardcoded.minigames_exam_title').replace('{pregunta}', examen['pregunta'])
    msg_queue.put(bot.send_message, chat_id, msg_text, parse_mode='Markdown')

def evaluar_ruleta(chat_id, user_id, texto, bot, msg_queue):
    resp = obtener_respuesta_ruleta(chat_id)
    if not resp:
        return
    if texto.strip().lower() != resp.lower():
        penalizar_puntos(user_id, 0.9)
        msg_queue.put(bot.send_message, chat_id, obtener_texto('hardcoded.minigames_42'))
        return
    puntos = random.randint(50, 150)
    actualizar_puntos_jugador(user_id, puntos)
    sector_pts = int(puntos * 1.5)
    sumar_puntos_grupo(chat_id, sector_pts)
    finalizar_ruleta(chat_id)
    msg_win = obtener_texto('hardcoded.minigames_ruleta_win').replace('{user_id}', str(user_id)).replace('{puntos}', str(puntos)).replace('{sector_pts}', str(sector_pts))
    msg_queue.put(bot.send_message, chat_id, msg_win)
