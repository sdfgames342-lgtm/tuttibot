import random
import logging
from core.db import get_connection

logger = logging.getLogger(__name__)

def mazo_truco_db():
    """Devuelve las 40 cartas del truco usando los nombres exactos de la DB."""
    conn = get_connection()
    # Filtramos por los rangos típicos del mazo español de 40
    rows = conn.execute(
        "SELECT nombre FROM stickers_cartas WHERE palo IS NOT NULL AND rango IN ('as','2','3','4','5','6','7','10','sota','caballo','rey')"
    ).fetchall()
    conn.close()
    return [r['nombre'] for r in rows]

def obtener_info_carta(nombre_carta):
    """Retorna toda la metadata de una carta desde la DB."""
    conn = get_connection()
    row = conn.execute(
        "SELECT rango, palo, valor_truco, valor_envido FROM stickers_cartas WHERE nombre = ?", 
        (nombre_carta,)
    ).fetchone()
    conn.close()
    return row

def enviar_carta(bot, chat_id, nombre_carta):
    """Envía un sticker buscando el file_id en la DB."""
    conn = get_connection()
    row = conn.execute(
        "SELECT file_id FROM stickers_cartas WHERE nombre = ?", 
        (nombre_carta,)
    ).fetchone()
    conn.close()
    
    if row and row['file_id']:
        try:
            bot.send_sticker(chat_id, row['file_id'])
            return True
        except Exception as e:
            logger.error(f"Error enviando sticker {nombre_carta}: {e}")
    
    bot.send_message(chat_id, f"🃏 [{nombre_carta.replace('_', ' ')}]")
    return False

def calcular_envido(mano):
    """Calcula el envido dinámico usando los valores de la DB."""
    puntos_por_palo = {}
    for nombre in mano:
        info = obtener_info_carta(nombre)
        if not info: continue
        palo = info['palo']
        puntos = info['valor_envido'] if info['valor_envido'] is not None else 0
        if palo not in puntos_por_palo:
            puntos_por_palo[palo] = []
        puntos_por_palo[palo].append(puntos)
    
    max_envido = 0
    for palo, valores in puntos_por_palo.items():
        if len(valores) >= 2:
            mejores = sorted(valores, reverse=True)[:2]
            score = 20 + sum(mejores)
        else:
            score = valores[0] if valores else 0
        if score > max_envido: max_envido = score
    return max_envido

def valor_truco(nombre_carta):
    """Retorna el peso jerárquico para el truco."""
    info = obtener_info_carta(nombre_carta)
    return info['valor_truco'] if info and info['valor_truco'] is not None else 0
