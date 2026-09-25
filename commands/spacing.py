from core.db import obtener_palabras_repaso
from datetime import datetime, timedelta
import sqlite3

def programar_repaso(user_id, palabra_ids, nivel_inicial=1):
    intervalos = [1, 2, 4, 7, 30]
    with sqlite3.connect('tutti_game.db') as conn:
        for pid in palabra_ids:
            conn.execute('\n                INSERT OR REPLACE INTO repaso_lexico \n                (user_id, palabra_id, nivel_dominio, ultimo_repaso, proximo_repaso)\n                VALUES (?, ?, ?, ?, ?)\n            ', (user_id, pid, nivel_inicial, datetime.now(), datetime.now() + timedelta(days=intervalos[nivel_inicial - 1])))
        conn.commit()

def obtener_palabras_para_revisar(user_id):
    return obtener_palabras_repaso(user_id)

def register_handlers(bot, *args, **kwargs):
    pass # Módulo de lógica interna
