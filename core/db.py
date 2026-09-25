import sqlite3
import os
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

# Ruta canónica: directorio padre de core/ + main_database.db
DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'main_database.db')

def conectar():
    """Devuelve una conexión con row_factory habilitado."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")  # mejor concurrencia
    return conn

# Alias para compatibilidad
get_db = conectar
conectar_db = conectar
get_connection = conectar

# ========== INICIALIZACIÓN ==========
def inicializar_db():
    """Crea las tablas si no existen (ya están creadas, pero por seguridad)."""
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS jugadores (
            user_id INTEGER PRIMARY KEY,
            nombre TEXT,
            puntos_historicos INTEGER DEFAULT 0,
            premium_status INTEGER DEFAULT 0,
            exp_date TEXT,
            sudo_level INTEGER DEFAULT 0,
            afinidad INTEGER DEFAULT 0
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS itsunario (
            user_id INTEGER PRIMARY KEY,
            tokens REAL DEFAULT 0,
            fichas INTEGER DEFAULT 0,
            partidas_ganadas_consecutivas INTEGER DEFAULT 0,
            nivel_ranking INTEGER DEFAULT 0
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS config_bot (
            clave TEXT PRIMARY KEY,
            valor TEXT
        )
    ''')
    # El resto de tablas se asume creadas; no se tocan.
    conn.commit()
    conn.close()

# ========== JUGADORES / USUARIOS ==========
def usuario_registrado(user_id):
    conn = conectar()
    row = conn.execute("SELECT 1 FROM jugadores WHERE user_id = ?", (user_id,)).fetchone()
    conn.close()
    return row is not None

def registrar_jugador(user_id, nombre="Desconocido"):
    conn = conectar()
    conn.execute(
        "INSERT OR IGNORE INTO jugadores (user_id, nombre) VALUES (?, ?)",
        (user_id, nombre)
    )
    conn.commit()
    conn.close()
    return True

def obtener_datos_usuario(user_id):
    conn = conectar()
    row = conn.execute(
        "SELECT nombre, puntos_historicos, afinidad, premium_status, exp_date, sudo_level FROM jugadores WHERE user_id = ?",
        (user_id,)
    ).fetchone()
    conn.close()
    if row:
        return {
            "nombre": row["nombre"],
            "puntos": row["puntos_historicos"],
            "afinidad": row["afinidad"],
            "premium_status": row["premium_status"],
            "exp_date": row["exp_date"],
            "sudo_level": row["sudo_level"]
        }
    return {"nombre": "Desconocido", "puntos": 0, "afinidad": 0}

def obtener_perfil_usuario(user_id):
    return obtener_datos_usuario(user_id)

def obtener_afinidad(user_id):
    conn = conectar()
    row = conn.execute("SELECT afinidad FROM jugadores WHERE user_id = ?", (user_id,)).fetchone()
    conn.close()
    return row["afinidad"] if row else 0

def actualizar_afinidad(user_id, delta):
    conn = conectar()
    conn.execute(
        "UPDATE jugadores SET afinidad = afinidad + ? WHERE user_id = ?",
        (delta, user_id)
    )
    conn.commit()
    conn.close()
    return True

def obtener_puntos_usuario(user_id):
    conn = conectar()
    row = conn.execute("SELECT puntos_historicos FROM jugadores WHERE user_id = ?", (user_id,)).fetchone()
    conn.close()
    return row[0] if row else 0

def actualizar_puntos_jugador(user_id, puntos):
    conn = conectar()
    conn.execute(
        "UPDATE jugadores SET puntos_historicos = puntos_historicos + ? WHERE user_id = ?",
        (puntos, user_id)
    )
    conn.commit()
    conn.close()
    return True

def obtener_puntos_usuario_en_grupo(*a):
    # Stub - parece no implementado, pero se deja por compatibilidad
    return 0

def set_sudo_level(user_id, level):
    conn = conectar()
    conn.execute("UPDATE jugadores SET sudo_level = ? WHERE user_id = ?", (level, user_id))
    conn.commit()
    conn.close()
    return True

def get_sudo_level(user_id):
    conn = conectar()
    row = conn.execute("SELECT sudo_level FROM jugadores WHERE user_id = ?", (user_id,)).fetchone()
    conn.close()
    return row[0] if row else 0

# ========== ITSUNARIO / ECONOMÍA ==========
def obtener_saldo_itsunario(user_id):
    conn = conectar()
    row = conn.execute("SELECT tokens, fichas FROM itsunario WHERE user_id = ?", (user_id,)).fetchone()
    conn.close()
    if row:
        return (row["tokens"], row["fichas"])
    return (0.0, 0)

def sumar_itsunario(user_id, tokens, fichas=0):
    conn = conectar()
    conn.execute(
        "INSERT INTO itsunario (user_id, tokens, fichas) VALUES (?, ?, ?) "
        "ON CONFLICT(user_id) DO UPDATE SET tokens = tokens + ?, fichas = fichas + ?",
        (user_id, tokens, fichas, tokens, fichas)
    )
    conn.commit()
    conn.close()
    return True

def canjear_tokens_por_fichas(user_id, tokens, fichas):
    conn = conectar()
    # Verificar saldo
    row = conn.execute("SELECT tokens FROM itsunario WHERE user_id = ?", (user_id,)).fetchone()
    if not row or row["tokens"] < tokens:
        conn.close()
        return False, 0
    conn.execute(
        "UPDATE itsunario SET tokens = tokens - ?, fichas = fichas + ? WHERE user_id = ?",
        (tokens, fichas, user_id)
    )
    conn.commit()
    conn.close()
    return True, fichas

# ========== CONFIGURACIÓN ==========
def get_config(clave, default=None):
    conn = conectar()
    row = conn.execute("SELECT valor FROM config_bot WHERE clave = ?", (clave,)).fetchone()
    conn.close()
    return row["valor"] if row else default

def set_config(clave, valor):
    conn = conectar()
    conn.execute(
        "INSERT OR REPLACE INTO config_bot (clave, valor) VALUES (?, ?)",
        (clave, str(valor))
    )
    conn.commit()
    conn.close()
    return True

def delete_config(clave):
    conn = conectar()
    conn.execute("DELETE FROM config_bot WHERE clave = ?", (clave,))
    conn.commit()
    conn.close()
    return True

# ========== GRUPOS / SALAS ==========
def grupo_activo(chat_id):
    conn = conectar()
    row = conn.execute("SELECT 1 FROM control_grupos WHERE chat_id = ? AND activo_en = 1", (chat_id,)).fetchone()
    conn.close()
    return row is not None

def activar_grupo(chat_id):
    conn = conectar()
    conn.execute(
        "INSERT OR IGNORE INTO control_grupos (chat_id, estado, activo_en) VALUES (?, 'ESPERA', 1)",
        (chat_id,)
    )
    conn.execute(
        "UPDATE control_grupos SET activo_en = 1 WHERE chat_id = ?",
        (chat_id,)
    )
    conn.commit()
    conn.close()
    return True

def desactivar_grupo(chat_id):
    conn = conectar()
    conn.execute("UPDATE control_grupos SET activo_en = 0 WHERE chat_id = ?", (chat_id,))
    conn.commit()
    conn.close()
    return True

def registrar_grupo(chat_id, nombre_grupo=None):
    conn = conectar()
    conn.execute(
        "INSERT OR IGNORE INTO control_grupos (chat_id, estado, nombre_grupo, fecha_registro) "
        "VALUES (?, 'ESPERA', ?, datetime('now'))",
        (chat_id, nombre_grupo)
    )
    conn.commit()
    conn.close()
    return True

def obtener_grupos_activos_ids():
    conn = conectar()
    rows = conn.execute("SELECT chat_id FROM control_grupos WHERE activo_en = 1").fetchall()
    conn.close()
    return [row[0] for row in rows]

def obtener_grupos_espera_inactivos(horas=24):
    conn = conectar()
    limite = datetime.now() - timedelta(hours=horas)
    rows = conn.execute(
        "SELECT chat_id FROM control_grupos WHERE estado = 'ESPERA' AND "
        "(ultima_partida IS NULL OR ultima_partida < ?)",
        (limite.isoformat(),)
    ).fetchall()
    conn.close()
    return [row[0] for row in rows]

def obtener_grupo_aleatorio_activo(*a):
    conn = conectar()
    row = conn.execute(
        "SELECT chat_id FROM control_grupos WHERE activo_en = 1 ORDER BY RANDOM() LIMIT 1"
    ).fetchone()
    conn.close()
    return row[0] if row else None

def contar_grupos_activos():
    conn = conectar()
    row = conn.execute("SELECT COUNT(*) FROM control_grupos WHERE activo_en = 1").fetchone()
    conn.close()
    return row[0] if row else 0

def contar_todos_grupos():
    conn = conectar()
    row = conn.execute("SELECT COUNT(*) FROM control_grupos").fetchone()
    conn.close()
    return row[0] if row else 0

def obtener_stats_grupo(chat_id):
    conn = conectar()
    row = conn.execute(
        "SELECT puntos_grupo, (SELECT COUNT(*) FROM contribuciones_grupo WHERE chat_id = ?) as usuarios "
        "FROM control_grupos WHERE chat_id = ?",
        (chat_id, chat_id)
    ).fetchone()
    conn.close()
    if row:
        return {"puntos": row["puntos_grupo"], "usuarios": row["usuarios"]}
    return {"puntos": 0, "usuarios": 0}

def obtener_puntos_grupo(chat_id):
    conn = conectar()
    row = conn.execute("SELECT puntos_grupo FROM control_grupos WHERE chat_id = ?", (chat_id,)).fetchone()
    conn.close()
    return row[0] if row else 0

def sumar_puntos_grupo(chat_id, puntos):
    conn = conectar()
    conn.execute(
        "UPDATE control_grupos SET puntos_grupo = puntos_grupo + ? WHERE chat_id = ?",
        (puntos, chat_id)
    )
    conn.commit()
    conn.close()
    return True

def penalizar_puntos(chat_id, puntos):
    return sumar_puntos_grupo(chat_id, -puntos)

def resetear_puntos_grupo(chat_id):
    conn = conectar()
    conn.execute("UPDATE control_grupos SET puntos_grupo = 0 WHERE chat_id = ?", (chat_id,))
    conn.commit()
    conn.close()
    return True

def obtener_jugadores_grupo(chat_id):
    conn = conectar()
    rows = conn.execute(
        "SELECT user_id, nombre FROM partida_jugadores WHERE chat_id = ?",
        (chat_id,)
    ).fetchall()
    conn.close()
    return [{"user_id": r["user_id"], "nombre": r["nombre"]} for r in rows]

def obtener_partidas_grupo(chat_id):
    conn = conectar()
    rows = conn.execute("SELECT * FROM partidas WHERE chat_id = ?", (chat_id,)).fetchall()
    conn.close()
    return [dict(r) for r in rows]

def obtener_partidas_jugador(user_id):
    conn = conectar()
    rows = conn.execute(
        "SELECT p.* FROM partidas p JOIN partida_jugadores pj ON p.chat_id = pj.chat_id "
        "WHERE pj.user_id = ?",
        (user_id,)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]

def obtener_ranking_interno_grupo(chat_id):
    conn = conectar()
    rows = conn.execute(
        "SELECT j.user_id, j.nombre, COALESCE(c.puntos_aportados, 0) as pts "
        "FROM jugadores j JOIN contribuciones_grupo c ON j.user_id = c.user_id "
        "WHERE c.chat_id = ? ORDER BY pts DESC LIMIT 10",
        (chat_id,)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]

def obtener_ranking_global_grupo():
    conn = conectar()
    rows = conn.execute(
        "SELECT g.chat_id, g.nombre_grupo, g.puntos_grupo "
        "FROM control_grupos g WHERE g.activo_en = 1 ORDER BY g.puntos_grupo DESC LIMIT 10"
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]

def obtener_top_puntos(limit=10):
    conn = conectar()
    rows = conn.execute(
        "SELECT user_id, nombre, puntos_historicos FROM jugadores "
        "ORDER BY puntos_historicos DESC LIMIT ?",
        (limit,)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]

def obtener_balance_puntos(*a):
    return 0  # No definido claramente, se mantiene

def grupo_en_espera(*a):
    return False  # Mantener lógica actual

# ========== PARTIDAS (TUTTIFRUTTI) ==========
def guardar_sala(chat_id, sala):
    conn = conectar()
    # Convertir el diccionario sala a campos de la tabla partidas
    estado = sala.get('estado', 'ESPERA')
    ronda = sala.get('ronda', 1)
    categorias = ','.join(sala.get('categorias', []))
    letra = sala.get('letra', '')
    inicio_epoch = sala.get('inicio_epoch', 0)
    bloques_procesados = sala.get('bloques_procesados', 0)
    jugadores = ','.join(str(uid) for uid in sala.get('jugadores', {}).keys())
    creador = sala.get('creador', 0)
    start_message_id = sala.get('start_message_id', None)

    conn.execute(
        "INSERT OR REPLACE INTO partidas (chat_id, estado, ronda, categorias, letra, "
        "inicio_epoch, bloques_procesados, jugadores, creador, start_message_id) "
        "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
        (chat_id, estado, ronda, categorias, letra, inicio_epoch, bloques_procesados,
         jugadores, creador, start_message_id)
    )
    # También guardar los jugadores en partida_jugadores
    for uid, nombre in sala.get('jugadores', {}).items():
        conn.execute(
            "INSERT OR IGNORE INTO partida_jugadores (chat_id, user_id, nombre) VALUES (?, ?, ?)",
            (chat_id, uid, nombre)
        )
    conn.commit()
    conn.close()
    return True

def cargar_salas():
    conn = conectar()
    rows = conn.execute("SELECT * FROM partidas WHERE estado != 'ESPERA'").fetchall()
    salas = {}
    for row in rows:
        jugadores_list = row["jugadores"].split(',') if row["jugadores"] else []
        jugadores_dict = {}
        for uid_str in jugadores_list:
            uid = int(uid_str)
            # Buscar nombre en partida_jugadores
            jrow = conn.execute(
                "SELECT nombre FROM partida_jugadores WHERE chat_id = ? AND user_id = ?",
                (row["chat_id"], uid)
            ).fetchone()
            jugadores_dict[uid] = jrow["nombre"] if jrow else str(uid)
        salas[row["chat_id"]] = {
            "estado": row["estado"],
            "ronda": row["ronda"],
            "categorias": row["categorias"].split(',') if row["categorias"] else [],
            "letra": row["letra"],
            "inicio_epoch": row["inicio_epoch"],
            "bloques_procesados": row["bloques_procesados"],
            "jugadores": jugadores_dict,
            "creador": row["creador"],
            "start_message_id": row["start_message_id"]
        }
    conn.close()
    return salas

def eliminar_sala(chat_id):
    conn = conectar()
    conn.execute("DELETE FROM partidas WHERE chat_id = ?", (chat_id,))
    conn.commit()
    conn.close()
    return True

# ========== MINIJUEGOS: EXAMEN, DUELO, LIBRO ==========
def examen_activo(chat_id):
    conn = conectar()
    row = conn.execute(
        "SELECT 1 FROM ruleta_rusa_salas WHERE chat_id = ? AND activa = 1", (chat_id,)
    ).fetchone()  # La tabla ruleta_rusa_salas se usa para exámenes sorpresa
    conn.close()
    return row is not None

def duelo_activo(chat_id):
    conn = conectar()
    row = conn.execute(
        "SELECT 1 FROM duelo_traduccion_salas WHERE chat_id = ? AND activa = 1", (chat_id,)
    ).fetchone()
    conn.close()
    return row is not None

def libro_activo(chat_id):
    conn = conectar()
    row = conn.execute(
        "SELECT 1 FROM biblioteca_global WHERE ultimo_grupo_id = ? AND estado = 'ASIGNADO'",
        (chat_id,)
    ).fetchone()
    conn.close()
    return row is not None

def ruleta_activa(chat_id):
    return examen_activo(chat_id)   # Ruleta rusa = exámenes sorpresa

def obtener_respuesta_examen(chat_id):
    conn = conectar()
    row = conn.execute(
        "SELECT respuesta FROM ruleta_rusa_salas WHERE chat_id = ? AND activa = 1",
        (chat_id,)
    ).fetchone()
    conn.close()
    return row[0] if row else ""

def obtener_pregunta_examen(chat_id):
    conn = conectar()
    row = conn.execute(
        "SELECT pregunta, respuesta FROM ruleta_rusa_salas WHERE chat_id = ? AND activa = 1",
        (chat_id,)
    ).fetchone()
    conn.close()
    if row:
        return {"pregunta": row["pregunta"], "correcta": row["respuesta"]}
    return {"pregunta": "", "correcta": ""}

def obtener_respuesta_duelo(chat_id):
    conn = conectar()
    row = conn.execute(
        "SELECT respuesta FROM duelo_traduccion_salas WHERE chat_id = ? AND activa = 1",
        (chat_id,)
    ).fetchone()
    conn.close()
    return row[0] if row else ""

def obtener_respuesta_ruleta(chat_id):
    return obtener_respuesta_examen(chat_id)

def obtener_libro_capturable(chat_id):
    conn = conectar()
    row = conn.execute(
        "SELECT id, respuesta_key, titulo FROM biblioteca_global "
        "WHERE estado = 'LIBRE' ORDER BY RANDOM() LIMIT 1"
    ).fetchone()
    conn.close()
    if row:
        return (row["id"], row["respuesta_key"], row["titulo"])
    return (None, "", "")

def obtener_pregunta_biblioteca(lang='es'):
    conn = conectar()
    row = conn.execute(
        "SELECT id, titulo, pregunta, respuesta_key FROM biblioteca_global WHERE idioma = ? "
        "ORDER BY RANDOM() LIMIT 1", (lang,)
    ).fetchone()
    conn.close()
    if row:
        return (row["id"], row["titulo"], row["pregunta"], row["respuesta_key"])
    return (1, "El Necronomicon", "Cual es el sentido de la vida?", "42")

def asignar_libro(libro_id, chat_id):
    conn = conectar()
    conn.execute(
        "UPDATE biblioteca_global SET ultimo_grupo_id = ?, estado = 'ASIGNADO', "
        "asignado_epoch = strftime('%s','now') WHERE id = ?",
        (chat_id, libro_id)
    )
    conn.commit()
    conn.close()
    return True

def capturar_libro(libro_id, user_id, chat_id):
    conn = conectar()
    conn.execute(
        "UPDATE biblioteca_global SET estado = 'CAPTURADO', ultimo_grupo_id = NULL WHERE id = ?",
        (libro_id,)
    )
    conn.commit()
    conn.close()
    return True

def liberar_libros_expirados(horas=6):
    conn = conectar()
    limite = (datetime.now() - timedelta(hours=horas)).timestamp()
    conn.execute(
        "UPDATE biblioteca_global SET estado = 'LIBRE', ultimo_grupo_id = NULL "
        "WHERE estado = 'ASIGNADO' AND asignado_epoch < ?",
        (limite,)
    )
    conn.commit()
    conn.close()
    return True

def registrar_duelo(chat_id, frase, respuesta):
    conn = conectar()
    conn.execute(
        "INSERT OR REPLACE INTO duelo_traduccion_salas (chat_id, activa, frase, respuesta, inicio_epoch) "
        "VALUES (?, 1, ?, ?, strftime('%s','now'))",
        (chat_id, frase, respuesta)
    )
    conn.commit()
    conn.close()
    return True

def finalizar_duelo(chat_id):
    conn = conectar()
    conn.execute("UPDATE duelo_traduccion_salas SET activa = 0 WHERE chat_id = ?", (chat_id,))
    conn.commit()
    conn.close()
    return True

def finalizar_ruleta(chat_id):
    conn = conectar()
    conn.execute("UPDATE ruleta_rusa_salas SET activa = 0 WHERE chat_id = ?", (chat_id,))
    conn.commit()
    conn.close()
    return True

def limpiar_duelo_expirado(chat_id):
    return finalizar_duelo(chat_id)

def limpiar_ruleta_expirada(chat_id):
    return finalizar_ruleta(chat_id)

# ========== PUNTOS (para juegos fuera de tuttifrutti) ==========
def sumar_puntos_grupo(chat_id, puntos):
    # Ya implementado en la sección de grupos
    return sumar_puntos_grupo(chat_id, puntos)

def penalizar_puntos(chat_id, puntos):
    return sumar_puntos_grupo(chat_id, -puntos)

def actualizar_puntos_jugador(user_id, puntos):
    return actualizar_puntos_jugador(user_id, puntos)

# ========== MARKETING / CANALES ==========
def actualizar_pin(bot, msg_queue):
    # Mantener lógica del kernel, se implementará allí
    pass

# ========== KEYS / PREMIUM ==========
def generar_key(tipo="standard"):
    import hashlib, uuid
    raw = uuid.uuid4().hex
    key = hashlib.sha256(raw.encode()).hexdigest()[:16]
    conn = conectar()
    conn.execute("INSERT INTO keys_activacion (key_hash, usada) VALUES (?, 0)", (key,))
    conn.commit()
    conn.close()
    return key

def validar_key(key):
    conn = conectar()
    row = conn.execute("SELECT usada FROM keys_activacion WHERE key_hash = ?", (key,)).fetchone()
    conn.close()
    return row is not None and row["usada"] == 0

# ========== OTRAS FUNCIONES ==========
def usuario_puede_descargar(user_id):
    conn = conectar()
    row = conn.execute(
        "SELECT 1 FROM descargas_ytmusic WHERE user_id = ? AND fecha_hora >= date('now')",
        (user_id,)
    ).fetchone()
    conn.close()
    return row is None

def registrar_descarga(user_id):
    conn = conectar()
    conn.execute("INSERT INTO descargas_ytmusic (user_id) VALUES (?)", (user_id,))
    conn.commit()
    conn.close()
    return True

def usuario_descarga_hoy(user_id):
    return usuario_puede_descargar(user_id) is False

def obtener_sticker_id(nombre):
    conn = conectar()
    row = conn.execute("SELECT file_unique_id FROM stickers_cartas WHERE nombre = ?", (nombre,)).fetchone()
    conn.close()
    return row[0] if row else None

def registrar_sticker(nombre, file_unique_id, emoji=None, set_name=None, metadata=None, creado_por=None,
                      palo=None, rango=None, idioma='frances', peso_truco=0):
    conn = conectar()
    conn.execute(
        "INSERT OR REPLACE INTO stickers_cartas (nombre, file_unique_id, emoji, set_name, metadata, "
        "creado_por, palo, rango, idioma, peso_truco) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
        (nombre, file_unique_id, emoji, set_name, metadata, creado_por, palo, rango, idioma, peso_truco)
    )
    conn.commit()
    conn.close()
    return True

def eliminar_sticker(nombre):
    conn = conectar()
    conn.execute("DELETE FROM stickers_cartas WHERE nombre = ?", (nombre,))
    conn.commit()
    conn.close()
    return True

def obtener_stickers():
    conn = conectar()
    rows = conn.execute("SELECT * FROM stickers_cartas").fetchall()
    conn.close()
    return [dict(r) for r in rows]

def obtener_palabras_repaso(user_id):
    conn = conectar()
    rows = conn.execute(
        "SELECT palabra_id, nivel_dominio, ultimo_repaso, proximo_repaso FROM repaso_lexico WHERE user_id = ?",
        (user_id,)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]

def jugador_en_otra_sala(user_id, chat_id_actual=None):
    conn = conectar()
    rows = conn.execute(
        "SELECT chat_id FROM partida_jugadores WHERE user_id = ? AND chat_id != ?",
        (user_id, chat_id_actual or "")
    ).fetchall()
    conn.close()
    return len(rows) > 0

# ========== FRASES PARA SIZAÑA (compatibilidad) ==========
FRASES_GLOBALES = [
    "Itsuki Online",
    "El Mainframe ha hablado.",
    "Tu lealtad está siendo evaluada.",
    "Cada comando fallido es una mancha en tu expediente.",
    "La mediocridad es una elección, no un destino.",
    "Si el código falla, el problema está entre la silla y el teclado.",
    "El Mainframe no olvida… y tampoco perdona.",
    "Has invocado al tribunal de la sintaxis.",
    "Tu AFK es directamente proporcional a tu utilidad.",
    "El silencio es el grito de los que no tienen argumentos."
]

# ========== FUNCIONES AUXILIARES PARA ADMIN ==========
def obtener_ultimo_grupo_activo():
    conn = conectar()
    row = conn.execute(
        "SELECT chat_id FROM control_grupos WHERE activo_en = 1 ORDER BY fecha_registro DESC LIMIT 1"
    ).fetchone()
    conn.close()
    return row[0] if row else None

def obtener_todos_chat_ids():
    conn = conectar()
    rows = conn.execute("SELECT chat_id FROM control_grupos").fetchall()
    conn.close()
    return [r[0] for r in rows]

def eliminar_grupo_por_id(chat_id):
    conn = conectar()
    conn.execute("DELETE FROM control_grupos WHERE chat_id = ?", (chat_id,))
    conn.commit()
    conn.close()

def obtener_ids_sin_nombre():
    conn = conectar()
    rows = conn.execute(
        "SELECT chat_id FROM control_grupos WHERE nombre_grupo IS NULL OR nombre_grupo = ''"
    ).fetchall()
    conn.close()
    return [r[0] for r in rows]

def actualizar_nombre_grupo(chat_id, nombre):
    conn = conectar()
    conn.execute(
        "UPDATE control_grupos SET nombre_grupo = ? WHERE chat_id = ?",
        (nombre, chat_id)
    )
    conn.commit()
    conn.close()

def obtener_grupos_paginados(limite, offset):
    conn = conectar()
    rows = conn.execute(
        "SELECT chat_id, nombre_grupo, CASE WHEN activo_en = 1 THEN 'ACTIVO' ELSE 'INACTIVO' END as estado "
        "FROM control_grupos ORDER BY fecha_registro DESC LIMIT ? OFFSET ?",
        (limite, offset)
    ).fetchall()
    conn.close()
    return [(r[0], r[1], r[2]) for r in rows]

def obtener_grupos_activos_con_nombre():
    conn = conectar()
    rows = conn.execute(
        "SELECT chat_id, nombre_grupo FROM control_grupos WHERE activo_en = 1"
    ).fetchall()
    conn.close()
    return [(r["chat_id"], r["nombre_grupo"]) for r in rows]

def obtener_grupos_activos_ids_por_idioma(idioma):
    conn = conectar()
    rows = conn.execute(
        "SELECT g.chat_id FROM control_grupos g INNER JOIN config_bot c ON c.clave = 'lang_chat_' || g.chat_id "
        "WHERE g.activo_en = 1 AND c.valor = ?",
        (idioma,)
    ).fetchall()
    conn.close()
    return [r[0] for r in rows]

def obtener_grupos_activos_con_nombre():
    conn = conectar()
    rows = conn.execute(
        "SELECT chat_id, nombre_grupo FROM control_grupos WHERE activo_en = 1"
    ).fetchall()
    conn.close()
    return [(r["chat_id"], r["nombre_grupo"]) for r in rows]

def obtener_grupos_activos_ids_por_idioma(idioma):
    conn = conectar()
    rows = conn.execute(
        "SELECT g.chat_id FROM control_grupos g "
        "INNER JOIN config_bot c ON c.clave = 'lang_chat_' || g.chat_id "
        "WHERE g.activo_en = 1 AND c.valor = ?",
        (idioma,)
    ).fetchall()
    conn.close()
    return [r[0] for r in rows]

def vender_fichas_por_tokens(user_id, fichas):
    """Convierte fichas a tokens aplicando comisión y límite diario."""
    conn = conectar()
    # Obtener parámetros de límites
    tasa = conn.execute("SELECT valor FROM itsunario_limites WHERE clave='ficha_a_token_tasa'").fetchone()
    comision_pct = conn.execute("SELECT valor FROM itsunario_limites WHERE clave='ficha_a_token_comision'").fetchone()
    limite_diario = conn.execute("SELECT valor FROM itsunario_limites WHERE clave='ficha_a_token_limite_diario'").fetchone()
    tasa = int(tasa[0]) if tasa else 10
    comision_pct = int(comision_pct[0]) if comision_pct else 10
    limite_diario = int(limite_diario[0]) if limite_diario else 100

    # Verificar saldo
    row = conn.execute("SELECT fichas FROM itsunario WHERE user_id = ?", (user_id,)).fetchone()
    if not row or row[0] < fichas:
        conn.close()
        return (False, "Fichas insuficientes")

    # Límite diario
    hoy = datetime.datetime.now().strftime('%Y-%m-%d')
    usado_hoy = conn.execute(
        "SELECT COALESCE(SUM(cantidad_fichas), 0) FROM itsunario_canjes WHERE user_id=? AND date(fecha)=? AND tipo='venta_fichas'",
        (user_id, hoy)).fetchone()[0]
    if usado_hoy + fichas > limite_diario:
        conn.close()
        return (False, f"Límite diario de venta excedido (máx {limite_diario} fichas)")

    tokens_brutos = fichas // tasa
    tokens_netos = int(tokens_brutos * (1 - comision_pct / 100))
    if tokens_netos <= 0:
        conn.close()
        return (False, "Cantidad insuficiente para generar al menos 1 token")

    conn.execute("UPDATE itsunario SET fichas = fichas - ?, tokens = tokens + ? WHERE user_id = ?",
                 (fichas, tokens_netos, user_id))
    conn.execute("INSERT INTO itsunario_canjes (user_id, tipo, cantidad_tokens, cantidad_fichas, comision) VALUES (?, 'venta_fichas', ?, ?, ?)",
                 (user_id, tokens_netos, fichas, comision_pct))
    conn.commit()
    conn.close()
    return (True, tokens_netos)
