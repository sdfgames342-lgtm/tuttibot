-- =====================================================================
-- ITSŲKI MAINFRAṀE - ESQUEMA DE BASE DE DATOS
-- =====================================================================

CREATE TABLE IF NOT EXISTS jugadores (
    user_id INTEGER PRIMARY KEY,
    nombre TEXT NOT NULL,
    puntos_historicos INTEGER DEFAULT 0,
    sudo_level INTEGER DEFAULT 0,
    afinidad INTEGER DEFAULT 0,
    premium_status INTEGER DEFAULT 0
);

CREATE TABLE IF NOT EXISTS partidas (
    chat_id TEXT PRIMARY KEY,
    estado TEXT DEFAULT 'ESPERA',
    ronda INTEGER DEFAULT 1,
    categorias TEXT,
    letra TEXT DEFAULT '',
    inicio_epoch INTEGER DEFAULT 0,
    bloques_procesados INTEGER DEFAULT 0,
    jugadores TEXT,
    creador INTEGER,
    start_message_id INTEGER,
    FOREIGN KEY (creador) REFERENCES jugadores(user_id)
);

CREATE TABLE IF NOT EXISTS respuestas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    sala_id TEXT NOT NULL,
    ronda INTEGER NOT NULL,
    categoria TEXT NOT NULL,
    user_id INTEGER NOT NULL,
    texto TEXT NOT NULL,
    votos INTEGER DEFAULT 0,
    FOREIGN KEY (user_id) REFERENCES jugadores(user_id),
    FOREIGN KEY (sala_id) REFERENCES partidas(chat_id)
);

CREATE TABLE IF NOT EXISTS calculo_puntos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    sala_id TEXT NOT NULL,
    ronda INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    categoria TEXT NOT NULL,
    puntos_ganados INTEGER DEFAULT 0,
    FOREIGN KEY (user_id) REFERENCES jugadores(user_id),
    FOREIGN KEY (sala_id) REFERENCES partidas(chat_id)
);

-- control_grupos con todas las columnas que el código utiliza
CREATE TABLE IF NOT EXISTS control_grupos (
    chat_id TEXT PRIMARY KEY,
    estado TEXT DEFAULT 'ESPERA',
    activo_en INTEGER DEFAULT 1,
    nombre_grupo TEXT,
    puntos_grupo INTEGER DEFAULT 0,
    fecha_activacion TIMESTAMP,
    ultima_partida TIMESTAMP,
    prioridad INTEGER DEFAULT 0,
    fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS metricas_marketing (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    evento TEXT NOT NULL,
    user_id INTEGER,
    chat_id TEXT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES jugadores(user_id)
);

CREATE TABLE IF NOT EXISTS log_eventos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    chat_id TEXT,
    user_id INTEGER,
    tipo_evento TEXT,
    latencia_ms INTEGER,
    valor_extra REAL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES jugadores(user_id)
);

CREATE TABLE IF NOT EXISTS config_bot (
    clave TEXT PRIMARY KEY,
    valor TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS stickers_cartas (
    nombre TEXT PRIMARY KEY,
    file_unique_id TEXT NOT NULL,
    emoji TEXT,
    set_name TEXT,
    metadata TEXT,
    creado_por INTEGER,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    peso_truco INTEGER DEFAULT 0,
    FOREIGN KEY (creado_por) REFERENCES jugadores(user_id)
);

CREATE TABLE IF NOT EXISTS partidas_guerra (
    chat_id TEXT PRIMARY KEY,
    estado_json TEXT NOT NULL,
    fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (chat_id) REFERENCES partidas(chat_id)
);

-- Índices
CREATE INDEX IF NOT EXISTS idx_respuestas_sala_ronda ON respuestas (sala_id, ronda);
CREATE INDEX IF NOT EXISTS idx_jugadores_user_id ON jugadores (user_id);
CREATE INDEX IF NOT EXISTS idx_partidas_estado ON partidas (estado);

-- Tablas de relación para partidas
CREATE TABLE IF NOT EXISTS partida_jugadores (
    chat_id TEXT NOT NULL,
    user_id INTEGER NOT NULL,
    nombre TEXT,
    PRIMARY KEY (chat_id, user_id),
    FOREIGN KEY (chat_id) REFERENCES partidas(chat_id),
    FOREIGN KEY (user_id) REFERENCES jugadores(user_id)
);

CREATE TABLE IF NOT EXISTS partida_categorias (
    chat_id TEXT NOT NULL,
    orden INTEGER NOT NULL,
    categoria TEXT NOT NULL,
    PRIMARY KEY (chat_id, orden),
    FOREIGN KEY (chat_id) REFERENCES partidas(chat_id)
);

-- Sistema económico Itsunario
CREATE TABLE IF NOT EXISTS itsunario (
    user_id INTEGER PRIMARY KEY,
    tokens INTEGER DEFAULT 0,
    fichas INTEGER DEFAULT 0,
    partidas_ganadas_consecutivas INTEGER DEFAULT 0,
    nivel_ranking INTEGER DEFAULT 0,
    FOREIGN KEY (user_id) REFERENCES jugadores(user_id)
);

CREATE TABLE IF NOT EXISTS itsunario_canjes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    tipo TEXT NOT NULL,
    cantidad_tokens INTEGER DEFAULT 0,
    cantidad_fichas INTEGER DEFAULT 0,
    comision INTEGER DEFAULT 0,
    fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES jugadores(user_id)
);

CREATE TABLE IF NOT EXISTS itsunario_limites (
    clave TEXT PRIMARY KEY,
    valor INTEGER NOT NULL
);

-- Banco (journaling)
CREATE TABLE IF NOT EXISTS banco_ledger (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    monto INTEGER NOT NULL,
    concepto TEXT,
    origen TEXT,
    fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES jugadores(user_id)
);

-- Inversiones a plazo fijo
CREATE TABLE IF NOT EXISTS inversiones (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    capital INTEGER NOT NULL,
    tasa_aplicada REAL NOT NULL,
    periodos INTEGER NOT NULL,
    fecha_inicio TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fecha_fin TIMESTAMP,
    activa INTEGER DEFAULT 1,
    FOREIGN KEY (user_id) REFERENCES jugadores(user_id)
);

-- Sizaña
CREATE TABLE IF NOT EXISTS frases_sizaña (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    trigger_tipo TEXT,
    perfil_objetivo TEXT,
    texto TEXT,
    peso_irritacion INTEGER DEFAULT 3
);

-- Keys de activación
CREATE TABLE IF NOT EXISTS keys_activacion (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    key_hash TEXT UNIQUE NOT NULL,
    generada_por INTEGER,
    usada INTEGER DEFAULT 0,
    expira TIMESTAMP,
    FOREIGN KEY (generada_por) REFERENCES jugadores(user_id)
);

-- Minijuegos: ruleta rusa
CREATE TABLE IF NOT EXISTS ruleta_rusa_salas (
    chat_id TEXT PRIMARY KEY,
    activa INTEGER DEFAULT 1,
    pregunta TEXT,
    respuesta TEXT,
    inicio_epoch REAL
);

-- Minijuegos: duelo traducción
CREATE TABLE IF NOT EXISTS duelo_traduccion_salas (
    chat_id TEXT PRIMARY KEY,
    activa INTEGER DEFAULT 1,
    frase TEXT,
    respuesta TEXT,
    inicio_epoch REAL
);

-- Minijuegos: biblioteca global
CREATE TABLE IF NOT EXISTS biblioteca_global (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    idioma TEXT,
    titulo TEXT,
    pregunta TEXT,
    respuesta_key TEXT,
    estado TEXT DEFAULT 'LIBRE',
    ultimo_grupo_id TEXT,
    asignado_epoch REAL
);

-- Repaso léxico
CREATE TABLE IF NOT EXISTS repaso_lexico (
    user_id INTEGER NOT NULL,
    palabra_id INTEGER NOT NULL,
    nivel_dominio INTEGER,
    ultimo_repaso TIMESTAMP,
    proximo_repaso TIMESTAMP,
    PRIMARY KEY (user_id, palabra_id),
    FOREIGN KEY (user_id) REFERENCES jugadores(user_id)
);

-- Contribuciones de puntos por grupo
CREATE TABLE IF NOT EXISTS contribuciones_grupo (
    chat_id TEXT NOT NULL,
    user_id INTEGER NOT NULL,
    puntos_aportados INTEGER DEFAULT 0,
    PRIMARY KEY (chat_id, user_id),
    FOREIGN KEY (chat_id) REFERENCES control_grupos(chat_id),
    FOREIGN KEY (user_id) REFERENCES jugadores(user_id)
);

-- Descargas YTMusic
CREATE TABLE IF NOT EXISTS descargas_ytmusic (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    fecha_hora TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES jugadores(user_id)
);

-- Límites Itsunario extra creados en migraciones (se incluyen directamente)
-- Los límites por defecto se insertan en core/db.py
