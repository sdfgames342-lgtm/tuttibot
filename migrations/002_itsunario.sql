-- Tokens Itsunario (moneda principal, ganada por logros)
CREATE TABLE IF NOT EXISTS itsunario (
    user_id INTEGER PRIMARY KEY,
    tokens INTEGER DEFAULT 0,
    fichas INTEGER DEFAULT 0,
    partidas_ganadas_consecutivas INTEGER DEFAULT 0,
    FOREIGN KEY (user_id) REFERENCES jugadores(user_id)
);

-- Registro de canjes (fichas, funciones)
CREATE TABLE IF NOT EXISTS itsunario_canjes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    tipo TEXT NOT NULL,            -- 'fichas', 'funcion'
    cantidad_tokens INTEGER DEFAULT 0,
    cantidad_fichas INTEGER DEFAULT 0,
    comision INTEGER DEFAULT 0,
    fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES jugadores(user_id)
);

-- Límites diarios de canje
CREATE TABLE IF NOT EXISTS itsunario_limites (
    clave TEXT PRIMARY KEY,
    valor INTEGER NOT NULL
);

-- Insertar límites por defecto
INSERT OR IGNORE INTO itsunario_limites (clave, valor) VALUES ('canje_fichas_max_diario', 100);
INSERT OR IGNORE INTO itsunario_limites (clave, valor) VALUES ('comision_canje_fichas', 5);  -- porcentaje
INSERT OR IGNORE INTO itsunario_limites (clave, valor) VALUES ('fichas_por_token', 10);
